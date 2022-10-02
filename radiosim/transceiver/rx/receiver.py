from radiosim.tools.fsm import FSM
from .demodulator import Demodulator
import queue
import threading
import zmq
import logging
log = logging.getLogger(__name__)


class Receiver(FSM):
	OFFLINE = "OFFLINE"
	SEARCH = "SEARCH"
	DEMOD = "DEMOD"
	states = [OFFLINE, SEARCH, DEMOD]

	object_counter = 0


	def __init__(self, modem, buffer_size=1024, iport=33333, timeout=1000):
		self._obj_idx = Receiver.object_counter
		Receiver.object_counter += 1
		self.loghdr = f"{self.__str__()} - "

		self.modem = modem
		self.register_states( self.states )
		self.initialize( self.OFFLINE )
		self.initialize_buffers( buffer_size )
		self.initialize_sockets( iport )
		self.timeout = timeout
		self.demodulator = Demodulator(self.modem, lambda : self.current_state, \
						 self.buf_front, self.buf_back, self.timeout)
		log.debug(f"New instance {self.__str__()} constructed as {self.__repr__()}")
		log.debug(f"Receiver object count = {Receiver.object_counter}")



	def __repr__(self):
		return f"Receiver(modem={self.modem.__repr__()}, buffer_size={self.buffer_size}, iport={self.iport}, timeout={self.timeout})"


	def __str__(self):
		return f"Rx{self._obj_idx}"


######################################################
# _____Initialization_____
# These methods are for initializing buffers, sockets,
# etc.
######################################################


	def initialize_buffers(self, buffer_size):
		self.buffer_size = buffer_size
		self.buf_front = queue.Queue( maxsize=self.buffer_size )
		self.buf_back  = queue.Queue( maxsize=self.buffer_size )
		log.info(self.loghdr + f"Buffers initialized with maxsize={self.buffer_size}")


	def initialize_sockets(self, iport):
		self.iport = iport
		tcp_lo = "tcp://127.0.0.1"
		self.zmq_context = zmq.Context()

		self.recv_socket = self.zmq_context.socket( zmq.PULL )
		pull_addr = f"{tcp_lo}:{self.iport}"
		self.recv_socket.connect( pull_addr )
		log.info(self.loghdr + f"Receive socket = {pull_addr}")


######################################################
# _____STARTUP_____
# These methods are for starting the receiver.
# Initially, it is put into a SEARCH state in which it
# listens for input data, passing it through a
# correlator looking for a preamble. When found, the
# receiver transitions into a DEMOD state.
######################################################


	@FSM.transition(OFFLINE, SEARCH)
	def start(self):
		log.info(self.loghdr + "Starting daemon receiving thread")
		self._recv_thread = threading.Thread( target=self._recv )
		self._recv_thread.daemon = True
		self._recv_thread.start()


	def _recv(self):
		log.info(self.loghdr + "Recv thread executing")
		while self.current_state != self.OFFLINE:
			if self.recv_socket.poll( self.timeout, zmq.POLLIN ):
				data = self.recv_socket.recv()
				self.buf_front.put(data)
			if self.current_state == self.SEARCH and not self.buf_front.empty():
				log.info(self.loghdr + "Data found in front buffer. Starting demodulation.")
				self.start_demodulation()
		log.debug(self.loghdr + "Terminating receive loop")



	@FSM.transition(SEARCH, DEMOD)
	def start_demodulation(self):
		log.info(self.loghdr + "Starting demodulator")
		self.demodulator.start()


######################################################
# _____STOPPING_____
# These methods are for stopping reception,
# clearing buffers, and transitioning to the OFFLINE 
# state
######################################################


	def stop(self):
		if self.current_state == self.SEARCH:
			self.stop_listening()
		elif self.current_state == self.DEMOD:
			self.stop_receiving()


	@FSM.transition(DEMOD, OFFLINE)
	def stop_receiving(self):
		log.info(self.loghdr + "Stopping receiving. Clearing buffers.")
		self.stop_listening()
		self.demodulator.join(2)    # clear front buffer + stop demodulator
		if not self.check_for_clear_buffers():
			log.warning(self.loghdr + "Failed to clear buffers")
		else:
			log.info(self.loghdr + "Buffers cleared")


	def stop_listening(self):
		log.info(self.loghdr + "Going offline")
		self._recv_thread.join(2) 


	def check_for_clear_buffers(self):
		return self.buf_front.empty() \
			and self.buf_back.empty()
