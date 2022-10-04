from radiosim.tools.fsm import FSM
from .node_proxy import NodeProxy
import numpy as np
import threading
import queue
import zmq
import logging
log = logging.getLogger(__name__)


class Channel(FSM):
	OFF = "OFF"
	ON = "ON"
	states = [OFF, ON]
	def __init__(self):
		self.register_states( self.states )
		self.initialize( self.OFF )
		self.nodes = {}
		self.ctx = zmq.Context()


	def __repr__(self):
		return f"Channel()"


	def add_node(self, txport=None, rxport=None):
		if txport is None and rxport is None:
			raise ValueError("Must provide one port for either rx or tx")
		self.nodes[f"{txport}{rxport}"] = NodeProxy(channel=self, txport=txport, rxport=rxport)
		log.info(f"Added node to channel: TX-port={txport}, RX-port={rxport}")


	def start(self):
		for key in self.nodes.keys():
			self.nodes[key].start()
		self._core_thread = threading.Thread( target=self._run_core )
		self._core_thread.daemon = True
		self._core_thread.start()


	@FSM.transition(OFF, ON)
	def _run_core(self):
		while self.current_state == self.ON:
			all_signals = []
			for key in self.nodes.keys():
				node = self.nodes[key]
				try:
					sig = node.txbuffer.get( block=False )
				except queue.Empty:
					continue # sig = np.zeros()
				all_signals.append( sig )
			if len(all_signals) == 0: continue
			total_signal = sum(all_signals)
			total_signal += self.generate_noise(len(sig))
			for key in self.nodes.keys():
				node = self.nodes[key]
				node.rxbuffer.put( total_signal )


	def generate_noise(self, num_samples):
		re = np.random.rand(num_samples) 
		im = np.random.rand(num_samples)
		return (re + 1j*im).astype(np.complex64)
