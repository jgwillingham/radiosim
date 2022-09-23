from .transmitter import Transmitter
from .receiver import Receiver
from tools.fsm import FSM

class Transceiver(FSM):
	def __init__(self, modem):
		self.modem = modem
