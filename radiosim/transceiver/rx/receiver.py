from tools.fsm import FSM
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

	def __init__(self, modem, buffer_size=1024, iport=33333):
		self.modem = modem
		self.register_states( self.states )
		self.initialize( self.OFFLINE )
		self.initialize_buffers( buffer_size )
		self.initialize_sockets( iport )


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
		log.info(f"Buffers initialized with maxsize={self.buffer_size}")

	def initialize_sockets(self, iport):
		self.iport = iport
		tcp_lo = "tcp://127.0.0.1"
		self.zmq_context = zmq.Context()

		self.recv_socket = self.zmq_context.socket( zmq.PULL )
		pull_addr = f"{tcp_lo}:{self.iport}"
		self.recv_socket.bind( pull_addr )
		log.info(f"Receive socket = {pull_addr}")


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
		log.info("Starting daemon receiving thread")
		self._recv_thread = threading.Thread( target=self._recv )
		self._recv_thread.daemon = True
		self._recv_thread.start()


	def _recv(self):
		log.info("Recv thread executing")
		while self.current_state != self.OFFLINE:
			data = self.recv_socket.recv()
			self.buf_front.put(data)
			if self.current_state == self.SEARCH and not self.buf_front.empty():
				self.start_demodulation()
				log.info("Data found in front buffer. Starting demodulation.")



	@FSM.transition(SEARCH, DEMOD)
	def start_demodulation(self):
		log.info("Starting demodulator")
		self.modulator = Demodulator(self.modem, self.current_state, \
						 self.buf_mid, self.buf_back)
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
