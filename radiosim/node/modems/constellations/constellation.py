import numpy as np
from itertools import product

class Constellation:
	"""
	Constellation class
	"""
	def __init__(self, symbol_map:dict):
		self.mapper = symbol_map


	def __repr__(self):
		return f"Constellation(symbol_map={self.mapper})"


	@property
	def mapper(self) -> dict:
		"""
		Dictionary containing the mapping from words to complex symbols
		"""
		return self._mapper


	@mapper.setter
	def mapper(self, mapping):
		_bps = np.log2( len(mapping) )
		if _bps != int(_bps):
			raise ValueError("Number of symbols in the mapping must be a power of 2")
		self._bps = int(_bps)
		self._mapper = mapping
		self._demapper = {symbol:word for word, symbol in mapping.items()}
		self._symbolset = np.array(list(self._demapper.keys()))
		self._bytewise_demapper = self._make_bytewise_demapper(mapping)


	@property
	def demapper(self) -> dict:
		"""
		Dictionary containing the mapping from complex symbols to words
		"""
		return self._demapper


	@property
	def bytewise_demapper(self) -> dict:
		"""
		Dictionary containing the mapping from sequences of complex symbols
		to corresponding single bytes
		"""
		return self._bytewise_demapper


	@property
	def symbolset(self):
		"""
		Set of symbols in the constellation
		"""
		return self._symbolset


	@property
	def bits_per_symbol(self):
		"""
		Number of bits per symbol
		"""
		return self._bps


	def _make_bytewise_demapper(self, mapper):
		"""
		Construct a bytewise demapper --- a dictionary which maps
		sequences of symbols to single bytes of data rather than
		few-bit (< 8-bit) words
		"""
		symbols = mapper.values()
		_8bword_demapper = self._demapper
		# Cartesian product SxSx...xS of symbol set S such that each element maps to 1 byte
		byte_length_seqs = product(symbols, repeat=8//self._bps) 
		bytewise_demapper = {}
		for sym_seq in byte_length_seqs:
			# for symbol sequence, get sequence of uint8 words (only last bps bits are meaningful)
			_8bword_seq = bytearray([_8bword_demapper[sym] for sym in sym_seq])
			# get only the relevant LSB of each uint8 word and group into byte-length sequences
			_8bword_seq_bits = np.unpackbits(_8bword_seq)
			byte_bits = [_8bword_seq_bits[i:i+8][-self._bps:] for i in range(0,len(_8bword_seq_bits), 8)]
			byte_bits = np.array(byte_bits).flatten()
			# pack byte-length sequences into bytes object
			bytewise_demapper[sym_seq] = np.packbits(byte_bits)[0].tobytes()
		return bytewise_demapper

