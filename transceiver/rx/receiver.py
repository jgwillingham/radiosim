from tools.fsm import FSM
import threading
from collections import deque


class Receiver(FSM):
	OFFLINE = "OFFLINE"
	LISTEN = "LISTEN"
	DEMOD = "DEMOD"
	states = [OFFLINE, LISTEN, DEMOD]

	def __init__(self, modem):
		self.modem = modem
		self.register_states(self.states)
		self.initialize(self.OFFLINE)
