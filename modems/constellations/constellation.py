from numpy import log2

class Constellation:
	"""
	Constellation class
	"""
	def __init__(self, symbol_map:dict):
		self.mapper = symbol_map


	@property
	def mapper(self) -> dict:
		"""
		Dictionary containing the mapping from words to complex symbols
		"""
		return self._mapper


	@mapper.setter
	def mapper(self, mapping):
		_bps = log2( len(mapping) )
		if _bps != int(_bps):
			raise ValueError("Number of symbols in the mapping must be a power of 2")
		self._bps = int(_bps)
		self._mapper = mapping
		self._demapper = {symbol:word for word, symbol in mapping.items()}


	@property
	def demapper(self) -> dict:
		"""
		Dictionary containing the mapping from complex symbols to words
		"""
		return self._demapper


	@property
	def bits_per_symbol(self):
		"""
		Number of bits per symbol
		"""
		return self._bps

