import threading
import logging
log = logging.getLogger(__name__)


class Packetizer(threading.Thread):
	def __init__(self, modem, state, inbuffer, outbuffer):
		super().__init__()
		self.modem = modem
		self.tx_state = state
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer


	def run(self):
		log.debug("Packetizer thread begin executing")
		while True:
			if self.tx_state != "TRANSMIT" and self.inbuffer.empty():
				break
			data = self.inbuffer.get() 
			# fill one payload of data
			# attach header here
			packet = data #tmp
			self.outbuffer.put(packet)
			self.inbuffer.task_done()
