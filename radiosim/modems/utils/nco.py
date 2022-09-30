import numpy as np

class NCO:
	"""
	Numerically controlled oscillator (NCO) class
	"""
	def __init__(self, f, phase=0):
		self._frequency = f
		self._phase = phase


	def __repr__(self):
		return f"NCO(f={self._frequency}, phase={self._phase})"


	@property
	def frequency(self):
		"""
		Frequency in cycles/sample
		"""
		return self._frequency


	@frequency.setter
	def frequency(self, value):
		if abs(value) >= 0.5:
			raise Warning("Frequency set above Nyquist")
		self._frequency = value


	@property
	def phase(self):
		return self._phase


	def get_samples(self, nsamples):
		phi = self._phase + self._frequency * np.arange(nsamples)
		self._phase += 2*np.pi*nsamples
		return np.exp(1j*phi)
