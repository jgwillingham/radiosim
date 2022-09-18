from abc import ABC, abstractmethod
import numpy as np

class Mapper(ABC):
	"""
	Abstract mapper class. Defines a stable framework for 
	creating symbol mappers for different modulation types 
	"""
	@property
	@abstractmethod
	def constellation(self):
		"""
		Symbol constellation
		"""
		pass


	@property
	@abstractmethod
	def bits_per_symbol(self):
		"""
		Number of bits per symbol
		"""
		pass


	@abstractmethod
	def map_word(self, word):
		"""
		Map a given word to the corresponding complex symbol
		"""
		pass


	def make_words(self, data):
		"""
		Split the given data into bit-sequences (words) which 
		can be mapped to corresponding symbols. Words are returned
		as unsigned 8-bit integers.
		"""
		if self.bits_per_symbol > 8:
			raise ValueError("Mapper only supports up to 8-bit wordsize")
		if not isinstance(data, bytearray):
			data = bytearray(data)
		bps = self.bits_per_symbol
		bits = np.unpackbits(data)
		bitshift = 8 - bps # np.packbits assumes the input is the first few MSB of 8-bit word. Shift to compensate.
		words = [np.packbits(bits[i-bps:i])[0] >> bitshift for i in range(bps, len(bits)+1, bps)]
		return np.array(words)


	def map(self, data):
		"""
		Map the provided data to a sequence of complex symbols
		"""
		words = self.make_words(data)
		symbols = [self.map_word(word) for word in words]
		return symbols
