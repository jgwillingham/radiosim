import threading
import struct
import numpy as np
import logging
log = logging.getLogger(__name__)


class Demodulator(threading.Thread):
	def __init__(self, modem, rx_state_query, inbuffer, outbuffer, timeout):
		super().__init__()
		self.modem = modem
		self.rx_state_query = rx_state_query
		self.inbuffer = inbuffer
		self.outbuffer = outbuffer
		self.timeout = timeout


	def run(self):
		log.debug("Demodulator thread begin executing")
		while self.rx_state_query() != "OFFLINE":
			# get data from buffer
			pbdata_bytes = self.inbuffer.get( self.timeout/1e3 )
			num_complex64s = len(pbdata_bytes)//8
			pb_interleaved = np.array(struct.unpack("ff"*num_complex64s, pbdata_bytes), dtype=np.complex64)
			pbdata = pb_interleaved[::2] + 1j*pb_interleaved[1::2]
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
		log.debug("Terminating demodulation loop")
