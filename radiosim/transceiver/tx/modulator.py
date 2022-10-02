import threading
import queue
import logging
log = logging.getLogger(__name__)

class Modulator(threading.Thread):

	object_counter = 0

	def __init__(self, modem, state_query, inbuffer, outbuffer, timeout):
		super().__init__()
		self._obj_idx = Modulator.object_counter
		Modulator.object_counter += 1
		self.modem = modem
		self.tx_state_query = state_query
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer
		self.timeout = timeout


	def __repr__(self):
		return f"Modulator(modem={self.modem.__repr__()}, state_query={self.tx_state_query.__repr__()}, \
			inbuffer={self.inbuffer.__repr__()}, outbuffer={self.outbuffer.__repr__()}, timeout={self.timeout})"


	def __str__(self):
		return f"Tx{self._obj_idx}"


	def run(self):
		log.debug(f" {self.__str__()} - Modulator thread begin executing")
		while True:
			if self.tx_state_query() != "TRANSMIT" and self.inbuffer.empty():
				break
			# get data
			try:
				data = self.inbuffer.get( timeout=self.timeout/1e3 )
			except queue.Empty:
				continue
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
		log.debug(f" {self.__str__()} - Terminating modulator")
