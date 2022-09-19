import numpy as np
from numpy import pi

class PulseShaper:
	SUPPORTED_PULSE_SHAPES = ["square", "rrc", "gaussian"]
	def __init__(self, shape="rrc"):
		self._define_filters()
		self.shape = shape


	@property
	def shape(self):
		return self._shape


	@shape.setter
	def shape(self, value):
		value = value.lower()
		if value not in self.SUPPORTED_PULSE_SHAPES:
			raise ValueError(f"Supported pulse shapes are {self.SUPPORTED_PULSE_SHAPES}")
		self.filter = self.filters[self._shape]
		self._shape = value


	def _define_filters(self):
		self.filters = {}
		self.filters["square"] = square_taps
		self.filters["rrc"] = rrc_taps
		self.filters["gaussian"] = gaussian_taps


	def square_taps(self):
		pass


	def rrc_taps(self, alpha, sps, ntaps):
		t = np.arange(ntaps)
		return np.sin( pi*t ) / (pi*t) * np.cos( alpha*pi*t ) / (1 - 4*alpha**2*t)


	def gaussian_taps(self):
		pass
