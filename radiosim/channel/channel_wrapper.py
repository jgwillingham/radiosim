import ctypes
import os

_lib = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) + "/build/lib/libchannel.so")

class Channel:
	def __init__(self):
		self.obj = _lib.channel_new()

	def add_node(self, txport, rxport, buffer_size=512):
		_lib.channel_add_node(self.obj, txport, rxport, buffer_size)

	def start(self):
		_lib.channel_start(self.obj)
