from abc import ABC, abstractmethod
from numpy import unpackbits, packbits

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
		can be mapped to corresponding symbols.
		Returns words as type uint8, e.g. 0b10 -> 2
		"""
		if not isinstance(data, bytearray):
			data = bytearray(data)
		bits = unpackbits(data)
		bps = self.bits_per_symbol
		words = [packbits(bits[i-bps:i])[0] for i in range(bps, len(bits)+1, bps)]
		return words


	def map(self, data):
		"""
		Map the provided data to a sequence of complex symbols
		"""
		words = self.make_words(data)
		symbols = [self.map_word(word) for word in words]
		return symbols
