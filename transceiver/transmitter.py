from tools.fsm import FSM
from .modulator import Modulator
from .packetizer import Packetizer
import queue
import threading
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
		self.iport = iport
		self.oport = oport


	def initialize_buffers(self, buffer_size):
		self.buffer_size = buffer_size
		self.buf_front = queue.Queue( maxsize=self.buffer_size )
		self.buf_mid   = queue.Queue( maxsize=self.buffer_size )
		self.buf_back  = queue.Queue( maxsize=self.buffer_size )
		log.debug(f"Buffers initialized with maxlen={self.buffer_size}")


	def start(self):
		self.start_listening_for_input()


	@FSM.transition(OFFLINE, READY)
	def start_listening_for_input(self):
		log.debug("Starting daemon listening thread")
		self._listen_thread = threading.Thread( target=self._listen_for_input )
		self._listen_thread.daemon = True
		self._listen_thread.start()


	def _listen_for_input(self):
		log.debug("Listening for input")
		while True:
			if self.current_state == self.READY and not self.buf_front.empty():
				self.start_transmitting()
			if self.current_state == self.OFFLINE:
				break
			# listen on some socket for data to store in the front buffer

	def start_sending_output(self):
		self._send_thread = threading.Thread( target=self._send_output )
		self._send_thread.start()


	def _send_output(self):
		log.debug(f"Sending output to destination port {self.oport}")
		while True:
			if self.state != self.TRANSMIT and self.back_buffer.empty(): break
			waveform_data = self.back_buffer.get()
			# send out socket
			self.back_buffer.task_done()


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


	def stop(self):
		if self.current_state == self.READY:
			self.stop_listening()
		elif self.current_state == self.TRANSMIT:
			self.stop_transmitting()


	@FSM.transition(TRANSMIT, OFFLINE)
	def stop_transmitting(self):
		log.debug("Stopping transmission. Clearing buffers.")
		self.stop_listening()
		self.packetizer.join()   # clear front buffer
		self.modulator.join()    # clear middle buffer
		self._send_thread.join() # clear back buffer
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

