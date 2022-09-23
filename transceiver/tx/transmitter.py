from tools.fsm import FSM
from .modulator import Modulator
from .packetizer import Packetizer
import queue
import threading
import zmq
import logging
log = logging.getLogger(__name__)


class Transmitter(FSM):
	"""
	IN --> Packetizer --> Modulator  --> OUT
	"""
	OFFLINE = "OFFLINE"
	READY = "READY"
	TRANSMIT = "TRANSMIT"
	states = [OFFLINE, READY, TRANSMIT]
	

	def __init__(self, modem, buffer_size=1024, iport=11111, oport=22222):
		self.modem = modem
		self.register_states( self.states )
		self.initialize( self.OFFLINE )
		self.initialize_buffers( buffer_size )
		self.initialize_sockets( iport, oport )

######################################################
# _____Initialization_____
# These methods are for initializing buffers, sockets,
# etc.
######################################################


	def initialize_buffers(self, buffer_size):
		self.buffer_size = buffer_size
		self.buf_front = queue.Queue( maxsize=self.buffer_size )
		self.buf_mid   = queue.Queue( maxsize=self.buffer_size )
		self.buf_back  = queue.Queue( maxsize=self.buffer_size )
		log.debug(f"Buffers initialized with maxlen={self.buffer_size}")


	def initialize_sockets(self, iport, oport):
		self.iport = iport
		self.oport = oport
		tcp_lo = "tcp://127.0.0.1"
		self.zmq_context = zmq.Context()

		self.listen_socket = self.zmq_context.socket( zmq.PULL )
		pull_addr = f"{tcp_lo}:{self.iport}"
		self.listen_socket.bind( pull_addr )
		log.info(f"Listen socket = {pull_addr}")

		self.transmit_socket = self.zmq_context.socket( zmq.PUSH )
		push_addr = f"{tcp_lo}:{self.oport}"
		self.transmit_socket.bind( push_addr )
		log.info(f"Output socket = {push_addr}")


######################################################
# _____STARTUP_____
# These methods are for starting the transmitter.
# Initially, it is put into a READY state in which it
# listens for input data on a socket. When data is
# received, it is put into a buffer where the next
# link in the signal chain (the packetizer) can get
# it. 
######################################################


	@FSM.transition(OFFLINE, READY)
	def start(self):
		log.debug("Starting daemon listening thread")
		self._listen_thread = threading.Thread( target=self._listen_for_input )
		#self._listen_thread.daemon = True
		self._listen_thread.start()


	def _listen_for_input(self):
		log.debug("Listening for input")
		while self.current_state != self.OFFLINE:
			# listen on input socket for data to store in the front buffer
			data = self.listen_socket.recv()
			self.buf_front.put(data)
			if self.current_state == self.READY and not self.buf_front.empty():
				self.start_transmitting()


	@FSM.transition(READY, TRANSMIT)
	def start_transmitting(self):
		log.debug("Starting modulator")
		self.modulator = Modulator(self.modem, self.current_state, \
						 self.buf_mid, self.buf_back)
		self.modulator.start()

		log.debug("Starting packetizer")
		self.packetizer = Packetizer(self.modem, self.current_state, \
						 self.buf_front, self.buf_mid)
		self.packetizer.start()

		self.start_sending_output()


	def start_sending_output(self):
		self._send_thread = threading.Thread( target=self._send_output )
		self._send_thread.start()


	def _send_output(self):
		log.debug(f"Sending output to destination port {self.oport}")
		while True:
			if self.state != self.TRANSMIT and self.back_buffer.empty(): break
			waveform_data = self.back_buffer.get()
			self.transmit_socket.send( waveform_data )
			self.back_buffer.task_done()


######################################################
# _____STOPPING_____
# These methods are for stopping transmission,
# clearing buffers, and transitioning to the OFFLINE 
# state
######################################################


	def stop(self):
		if self.current_state == self.READY:
			self.stop_listening()
		elif self.current_state == self.TRANSMIT:
			self.stop_transmitting()


	@FSM.transition(TRANSMIT, OFFLINE)
	def stop_transmitting(self):
		log.debug("Stopping transmission. Clearing buffers.")
		self.stop_listening()
		self.packetizer.join()   # clear front buffer + stop packetizer
		self.modulator.join()    # clear middle buffer + stop modulator
		self._send_thread.join() # clear back buffer + stop output
		if not self.check_for_clear_buffers():
			log.warning("Failed to clear buffers")
		else:
			log.debug("Buffers cleared")


	@FSM.transition(READY, OFFLINE)
	def stop_listening(self):
		log.debug("Going offline")
		# shutdown socket here
		self._listen_thread.join()


	def check_for_clear_buffers(self):
		return self.buf_front.empty() \
			and self.buf_mid.empty() \
			and self.buf_back.empty()

