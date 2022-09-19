from abc import ABC, abstractmethod
from .constellations import Constellation
from .utils import PulseShaper
import numpy as np
from scipy import signal as dsp

class Modem(ABC):
	"""
	Abstract modem class. Defines a stable framework for 
	creating symbol mappers for different modulation types 
	"""
	@property
	@abstractmethod
	def constellation(self) -> Constellation:
		"""
		Symbol constellation
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
		return np.array(words)


	def map(self, data):
		"""
		Map the provided data to a sequence of complex symbols
		"""
		words = self.make_words(data)
		symbols = [self.constellation.mapper[word] for word in words]
		return np.array(symbols)


	def demap(self, symbols):
		"""
		Demap the given symbols to the corresponding byte sequence
		"""
		words = [self.constellation.demapper[sym] for sym in symbols]
		data = np.array(words).flatten()
		return bytearray(data)


##################################################################
# _____PULSE_SHAPING_____
# These next methods are for pulse shaping the symbols into a 
# pulse-train to obtain the baseband waveform.
##################################################################


	@property
	def pulse_shaper(self):
		return self._pulse_shaper


	@property
	def pulse_shape(self):
		return self._pulse_shape


	@pulse_shape.setter
	def pulse_shape(self, value):
		if not hasattr(self, "_pulse_shaper"):
			self._pulse_shaper = PulseShaper(value)
		else:
			self._pulse_shaper.shape = value
		self._pulse_shape = shape
