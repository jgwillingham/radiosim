from .modem import Modem
from .constellations import qpsk_constellation
import numpy as np

class QPSKModem(Modem):
	def __init__(self, sps=8):
		self._constellation = qpsk_constellation
		self._sps = sps
		self.psparams = {"sps":sps, 
				"num_positive_lobes":8, 
				"alpha":0.33}
		self.pulse_shape_filter = self.get_pulse_filter(**self.psparams)	
		rrc = self.pulse_shape_filter
		self.matched_filter = rrc / np.linalg.norm(rrc)**2


	def __repr__(self):
		return f"QPSKModem(sps={self._sps})"


	@property
	def constellation(self):
		return self._constellation


	@property
	def samples_per_symbol(self):
		return self._sps
