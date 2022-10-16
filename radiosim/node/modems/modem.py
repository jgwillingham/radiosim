from abc import ABC, abstractmethod
import numpy as np
from .constellations import Constellation
from .utils.pulse_shaping import rrc_filter, SUPPORTED_PULSE_SHAPES, DEFAULT_SPS
from .utils.nco import NCO
from .utils.ofdm import OFDM

class Modem(ABC):
	"""
	Abstract base class for all modems. Defines a stable framework for 
	all modulation and demodulation functionality.
	"""
	@property
	@abstractmethod
	def constellation(self) -> Constellation:
		"""
		Symbol constellation
		"""
		pass


	@property
	@abstractmethod
	def ofdm_active(self) -> bool:
		"""
		True if OFDM is used, otherwise false
		"""
		pass


##################################################################
# _____MAPPER_____
# These next methods are the implementation of the mapper and
# demapper (maps between bit sequences (words) and complex symbols
# in the constellation)
##################################################################


	def make_words(self, data):
		"""
		Split the given data into bit-sequences (words) which 
		can be mapped to corresponding symbols. Words are returned
		as unsigned 8-bit integers.
		"""
		if self.constellation.bits_per_symbol > 8:
			raise ValueError("Mapper only supports up to 8-bit wordsize")
		if not isinstance(data, bytearray):
			data = bytearray(data)
		bps = self.constellation.bits_per_symbol
		bits = np.unpackbits(data)
		bitshift = 8 - bps # np.packbits assumes the input is the first few MSB of 8-bit word. Shift to compensate.
		words = [np.packbits(bits[i-bps:i])[0] >> bitshift for i in range(bps, len(bits)+1, bps)]
		return np.array(words, dtype=np.uint8)


	def map(self, data):
		"""
		Map the provided data to a sequence of complex symbols
		"""
		words = self.make_words(data)
		symbols = [self.constellation.mapper[word] for word in words]
		return np.array(symbols, dtype=np.complex64)


	def demap(self, symbols) -> bytes:
		"""
		Demap the given symbols to the corresponding byte sequence
		"""
		spb = 8//self.constellation.bits_per_symbol # symbols per byte
		if len(symbols) % spb != 0:
			raise ValueError("For bytewise demapping, the input symbols must correspond" + \
					" to an integer number of bytes")
		byte_symbol_seqs = [tuple(symbols[i:i+spb]) for i in range(0, len(symbols), spb)]
		raw_byte_list = [self.constellation.bytewise_demapper[seq] for seq in byte_symbol_seqs]
		rawdata = b''
		for byt in raw_byte_list: 
			rawdata += byt
		return rawdata


##################################################################
# _____PULSE_SHAPING_____
# These next methods are for pulse shaping the symbols into a 
# pulse-train to obtain the baseband waveform.
##################################################################


	def get_pulse_filter(self, **params):
		"""
		Returns the filter coefficients used in the pulse shaping filter.
		"""
		if "sps" in params.keys():
			self._sps = params["sps"]
		else:
			self._sps = DEFAULT_SPS
		return rrc_filter(**params)


	def apply_pulse_filter(self, symbols, psfilter):
		"""
		Applies the FIR pulse shaping filter to the provided symbols.
		In the process, the symbols are upsampled by the number of
		samples per symbol.
		"""
		upsampled_symbols = np.zeros(len(symbols)*self._sps, dtype=np.complex64)
		upsampled_symbols[::self._sps] = symbols
		bb_signal = np.convolve(upsampled_symbols, psfilter, 'same')
		return bb_signal.astype(np.complex64)


	def apply_matched_filter(self, bbsig, mfilter):
		"""
		Performs a simple convolution for matched filtering on receive side
		"""
		return np.convolve(bbsig, mfilter, 'same').astype(np.complex64)


##################################################################
# _____UP/DOWN_CONVERSION_____
# These methods are for upconverting a baseband signal to passband
# or conversely downconverting a passband signal to baseband
##################################################################


	@property
	def center_freq(self):
		try:
			return self._center_freq
		except:
			raise AttributeError("Center frequency is not set")


	@center_freq.setter
	def center_freq(self, value):
		if hasattr(self, "_nco"):
			self._nco.frequency = value
		else:
			self._nco = NCO(f=value)


	def upconvert(self, bb_signal):
		nsamples = len(bb_signal)
		pb_signal = bb_signal * self._nco.get_samples(nsamples)
		return pb_signal.astype(np.complex64)


	def downconvert(self, pb_signal):
		nsamples = len(pb_signal)
		bb_signal = pb_signal * np.conj(self._nco.get_samples(nsamples))
		return bb_signal.astype(np.complex64)


##################################################################
# _____Receiving_____
# These methods are for translating the noise-corrupted demodulated
# symbols to the best estimate of the true symbols
##################################################################


	def get_euclidean_estimates(self, complex_bbdata):
		"""
		Get estimates of the true symbols given the input complex
		baseband data by using the minimum Euclidean distance
		"""
		symbolset = self.constellation.symbolset
		closest_symbols = [symbolset[np.argmin(abs(sym - symbolset))] for sym in complex_bbdata]
		return closest_symbols
