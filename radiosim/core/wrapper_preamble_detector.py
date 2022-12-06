import ctypes
import os

_lib = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) +"/build/lib/libpreamble_detector.so")

class PreambleDetector:
	def __init__(self, iport, buffer_size):
		self.obj = _lib.preamble_detector_new(iport, buffer_size)

	def start(self):
		_lib.preamble_detector_start(self.obj)
