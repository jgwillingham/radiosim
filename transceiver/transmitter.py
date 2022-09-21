from tools.fsm import FSM
from collections import deque
import threading
import logging
log = logging.getLogger(__name__)


class Transmitter(FSM):
	"""
	IN --> Packetize --> Modulate  --> OUT
	"""
	OFFLINE = "OFFLINE"
	READY = "READY"
	TRANSMIT = "TRANSMIT"
	states = [OFFLINE, READY, TRANSMIT]
	

	def __init__(self, modem, buffer_size=1024):
		self.modem = modem
		self.register_states( self.states )
		self.initialize( self.OFFLINE )
		self.initialize_buffers(buffer_size)


	def initialize_buffers(selfi, buffer_size):
		log.debug(f"Buffers initialized with maxlen={self.buffer_size}")
		self.buffer_size = buffer_size
		self.buf_front = deque( maxlen=self.buffer_size )
		self.buf_back  = deque( maxlen=self.buffer_size )


	def start(self):
		self.start_listening_for_input()


	@FSM.transition(OFFLINE, READY)
	def start_listening_for_input(self):
		log.debug("Starting daemon listening thread")
		self._listen_thread = threading.Thread(target = self._listen_for_input)
		self._listen_thread.daemon = True
		self._listen_thread.start()


	def _listen_for_input(self):
		log.debug("Listening for input...")
		while True:
			if self.current_state == self.READY and len(self.buf_front) != 0:
				self.start_transmitting()
			# listen on some socket for data to store in the front buffer


	@FSM.transition(READY, TRANSMIT)
	def start_transmitting(self):
		self._packetize_thread = threading.Thread( target = self.packetize )
		self._modulate_thread = threading.Thread( target = self.modulate )
		self._packetize_thread.start()
		self._modulate.start()


	def packetize(self):
		pass


	 def modulate(self):
		pass


	@FSM.transition(TRANSMIT, READY)
	def stop_transmitting(self):
		log.debug("Stopping transmission. Clearing front buffer.")
		self._packetize_thread.join()
		self._modulate_thread.join()
		self.stop_listening()


	@FSM.transition(READY, OFFLINE)
	def stop_listening(self):
		log.debug("Turning off transmitter")
		self._listen_thread.join()


