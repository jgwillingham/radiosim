from abc import ABC
from functools import wraps
import logging
log = logging.getLogger(__name__)


class StateError(Exception):
	pass


class FSM(ABC):
	"""
	Abstract base class for finite-state machines. The key functionality 
	provided by FSM is a decorator @transition(*,*) which wraps transition 
	functions so that all the statefulness is handled effortlessly and with
	easy to understand code.

	Example usage might look like this:
	>>> class MyMachine(FSM):
	...	STATE1 = "STATE1"
	...	STATE2 = "STATE2"
	...	STATE3 = "STATE3"
	...	states = [STATE1, STATE2, STATE3]
	...	def __init__(self):
	...		self.register_states(self.states)
	...		self.initialize(self.STATE1) # sets state to STATE1
	...
	...	@FSM.transition(STATE1, STATE2)
	...	def first_transition(self, *args, **kwargs):
	...		... # this triggers a state change from STATE1 --> STATE2
	...
	...	@FSM.transition(STATE2, STATE3)
	...	def second_transition(self, *args, **kwargs):
	...		... # this triggers a state change from STATE2 --> STATE3
	...
	...	@FSM.transition(STATE3, STATE1)
	...	def third_transition(self, *args, **kwargs):
	...		... # this triggers a state change from STATE3 --> STATE1
	"""

	@property
	def current_state(self):
		return self._state


	def get_states(self):
		return self._states


	def register_states(self, states):
		if not hasattr(self, "_states"):
			self._states = ()
		if isinstance(states, str):
			self._states += (states,)
		else:
			self._states += tuple(states)


	def initialize(self, initial_state):
		if initial_state in self._states:
			self._state = initial_state
			log.debug(f"Initialized FSM in state {self._state}")
		else:
			raise StateError(f"{initial_state} is not a valid state.")


	def transition(state1, state2):
		def decorator(func):
			@wraps(func)
			def wrapper(*args, **kwargs):
				_self = args[0]
				isvalid = _self._state == state1 and \
					state1 in _self._states and \
					state2 in _self._states
				if isvalid:
					log.debug(f"Trigger transition: {state1} --> {state2}")
					_self._state = state2
					func(*args, **kwargs)
				else:
					raise StateError(f"Transition {state1} --> {state2} is invalid. \
							Current state is {_self._state}")
			return wrapper
		return decorator
