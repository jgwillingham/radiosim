from .mapper import Mapper

class QPSKModulator(Mapper):
	GRAY_CODE = {
		0b00 : -1 - 1j,
		0b01 : -1 + 1j,
		0b10 :  1 - 1j,
		0b11 :  1 + 1j}
	def __init__(self):
		self._constellation = self.GRAY_CODE
		self._bits_per_symbol = 2

	@property
	def constellation(self):
		return self._constellation

	@property
	def bits_per_symbol(self):
		return self._bits_per_symbol

	def map_word(self, word):
		return self.constellation[word]
