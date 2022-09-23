import threading


class Packetizer(threading.Thread):
	def __init__(self, modem, state, inbuffer, outbuffer):
		self.modem = modem
		self.tx_state = state
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer


	def run(self):
		while True:
			if self.tx_state != "TRANSMIT" and self.inbuffer.empty():
				break
			data = self.inbuffer.get() 
			# fill one payload of data
			# attach header here
			packet = data #tmp
			self.outbuffer.put(packet)
			self.inbuffer.task_done()
