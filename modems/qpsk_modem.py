from .modem import Modem
from .constellations import QPSKConstellation

class QPSKModem(Modem):
	def __init__(self):
		self._constellation = QPSKConstellation
	
	@property
	def constellation(self):
		return self._constellation
