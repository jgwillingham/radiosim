import threading
import queue
import logging
log = logging.getLogger(__name__)


class Demodulator(threading.Thread):

	object_counter = 0

	def __init__(self, modem, state_query, inbuffer, outbuffer, timeout):
		super().__init__()
		self._obj_idx = Demodulator.object_counter
		Demodulator.object_counter += 1
		self.modem = modem
		self.rx_state_query = state_query
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer
		self.timeout = timeout


	def __repr__(self):
		return f"Demodulator(modem={self.modem.__repr__()}, state_query={self.rx_state_query.__repr__()}, \
			inbuffer={self.inbuffer.__repr__()}, outbuffer={self.outbuffer.__repr__()}, timeout={self.timeout})"


	def __str__(self):
		return f"Rx{self._obj_idx}"


	def run(self):
		log.debug(f" {self.__str__()} - Demodulator thread begin executing")
		while True:
			if self.rx_state_query() != "DEMOD" and self.inbuffer.empty(): break
			# get data from buffer
			try:
				pbdata = self.inbuffer.get( timeout=self.timeout/1e3 )
			except queue.Empty:
				continue
			# downconvert to baseband
			bbdata = self.modem.downconvert(pbdata)
			# clean signal with matched filter
			bbdata_clean = self.modem.apply_matched_filter(bbdata, self.modem.matched_filter)
			# phase synchronization?
			phase_offset = 2
			# get symbol measurements and estimate true symbols
			symbolmeas = bbdata_clean[phase_offset::self.modem.samples_per_symbol]
			symbols = self.modem.get_euclidean_estimates(symbolmeas)
			# demap symbols to bytes
			databytes = self.modem.demap(symbols)
			# put bytes in the output buffer
			self.outbuffer.put(databytes)
			# mark task as done
			self.inbuffer.task_done()
		log.debug(f" {self.__str__()} - Terminating demodulator")
