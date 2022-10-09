import threading
import queue
import logging
log = logging.getLogger(__name__)

class Packetizer(threading.Thread):

	object_counter = 0

	def __init__(self, modem, state_query, inbuffer, outbuffer, timeout):
		super().__init__()
		self._obj_idx = Packetizer.object_counter
		Packetizer.object_counter += 1
		self.modem = modem
		self.tx_state_query = state_query
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer
		self.timeout = timeout


	def __repr__(self):
		return f"Packetizer(modem={self.modem.__repr__()}, state_query={self.state_query.__repr__()}, \
			inbuffer={self.inbuffer.__repr__()}, outbuffer={self.outbuffer.__repr__()}, timeout={self.timeout})"


	def __str__(self):
		return f"Tx{self._obj_idx}"


	def run(self):
		log.debug(f"{self.__str__()} - Packetizer thread begin executing")
		while True:
			if self.tx_state_query() != "TRANSMIT" and self.inbuffer.empty():
				break
			try:
				data = self.inbuffer.get( timeout=self.timeout/1e3 )
			except queue.Empty:
				continue
			# fill one payload of data
			# attach header here
			packet = data #tmp
			self.outbuffer.put(packet)
			self.inbuffer.task_done()
		log.debug(f"{self.__str__()} - Terminating packetizer thread")
