import unittest
from radiosim.tools.fsm import FSM, StateError


class StateMachine(FSM):
	STATE_A = "STATE_A"
	STATE_B = "STATE_B"
	STATE_C = "STATE_C"
	STATE_D = "STATE_D"
	states = [STATE_A, STATE_B, STATE_C, STATE_D]
	def __init__(self):
		self.register_states(self.states)
		self.initialize(self.STATE_A)
	@FSM.transition(STATE_A, STATE_B)
	def a_to_b(self, *args, **kwargs):
		pass
	@FSM.transition(STATE_B, STATE_C)
	def b_to_c(self, *args, **kwargs):
		pass
	@FSM.transition(STATE_C, STATE_D)
	def c_to_d(self, *args, **kwargs):
		pass
	@FSM.transition(STATE_C, STATE_A)
	def c_to_a(self, *args, **kwargs):
		pass
	@FSM.transition(STATE_C, STATE_D)
	def c_to_d(self, *args, **kwargs):
		pass


class FSMTesting(unittest.TestCase):
	def test_state_transitions(self):
		"""
		--\t\tFSM state transitions work and errors are thrown as expected
		"""
		sm = StateMachine()
		self.assertTrue(sm.current_state == sm.STATE_A)
		self.assertRaises(StateError, sm.b_to_c)
		sm.a_to_b()
		self.assertTrue(sm.current_state == sm.STATE_B)
		sm.b_to_c()
		self.assertTrue(sm.current_state == sm.STATE_C)
		sm.c_to_a()
		self.assertTrue(sm.current_state == sm.STATE_A)
		sm.a_to_b()
		sm.b_to_c()
		sm.c_to_d()
		self.assertRaises(StateError, sm.c_to_d)
		self.assertTrue(sm.current_state == sm.STATE_D)


if __name__=="__main__":
	unittest.main()
	
