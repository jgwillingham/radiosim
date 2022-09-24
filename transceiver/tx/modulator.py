import threading
import logging
log = logging.getLogger(__name__)

class Modulator(threading.Thread):
	def __init__(self, modem, state, inbuffer, outbuffer):
		super().__init__()
		self.modem = modem
		self.tx_state = state
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer


	def run(self):
		log.debug("Modulator thread begin executing")
		while True:
			if self.tx_state != "TRANSMIT" and self.inbuffer.empty():
				break
			# get data
			data = self.inbuffer.get()
			# map to complex symbols
			symbols = self.modem.map(data)
			# pulse shape
			bb_signal = self.modem.apply_pulse_filter(symbols, self.modem.pulse_shape_filter)
			# upconvert
			pb_signal = self.modem.upconvert(bb_signal)
			# put in output buffer
			self.outbuffer.put(pb_signal)
			# make task as done
			self.inbuffer.task_done()
