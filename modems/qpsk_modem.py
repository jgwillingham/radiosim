from .modem import Modem
from .constellations import qpsk_constellation

class QPSKModem(Modem):
	def __init__(self):
		self._constellation = qpsk_constellation
	
	@property
	def constellation(self):
		return self._constellation
