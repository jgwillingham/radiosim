import threading
import logging
log = logging.getLogger(__name__)


class Demodulator(threading.Thread):
	def __init__(self, modem, rx_state, inbuffer, outbuffer):
		super().__init__()
		self.modem = modem
		self.rx_state = rx_state
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer


	def run(self):
		log.debug("Demodulator thread being executing")
		while self.rx_state != "OFFLINE":
			# get data from buffer
			rawdata = self.inbuffer.get()
			# downconvert to baseband
			data = self.modem.downconvert(rawdata)
			# extract symbols with matched filter
			symbols = self.modem.matched_filter(rawdata)
			# demap symbols to words
			words = self.modem.demap(symbols)
			# put words in the output buffer
			self.outbuffer.put(words)
			# mark task as done
			self.inbuffer.task_done()
