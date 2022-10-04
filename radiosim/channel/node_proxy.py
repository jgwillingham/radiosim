import numpy as np
import threading
import zmq
import struct
import queue
import logging
log = logging.getLogger(__name__)

 
class NodeProxy:
	def __init__(self, channel, txport=None, rxport=None, buffer_size=1024, timeout=1000):
		self.channel = channel
		self.initialize_buffers( buffer_size )
		self.initialize_sockets( txport, rxport )
		self.timeout = timeout


	def __repr__(self):
		return f"NodeProxy(channel={self.channel.__repr__()}, txport={self.txport}, rxport={self.rxport}, buffer_size={self.buffer_size}, timeout={self.timeout})"


	def initialize_buffers(self, buffer_size):
		self.buffer_size = buffer_size
		self.txbuffer = queue.Queue( maxsize=buffer_size )
		self.rxbuffer = queue.Queue( maxsize=buffer_size )


	def initialize_sockets(self, txport, rxport):
		self.txsocket = None
		self.rxsocket = None

		tcp_lo = "tcp://127.0.0.1"
		if txport is not None:
			self.txsocket = self.channel.ctx.socket( zmq.PULL )
			self.txsocket.connect( f"{tcp_lo}:{txport}" )
		if rxport is not None:
			self.rxsocket = self.channel.ctx.socket( zmq.PUSH )
			self.rxsocket.bind( f"{tcp_lo}:{rxport}" )


	def start(self):
		log.debug("Starting NodeProxy sockets")
		if self.txsocket is not None:
			self._listen_thread = threading.Thread( target=self._listen )
			self._listen_thread.daemon = True
			self._listen_thread.start()
		if self.rxsocket is not None:
			self._send_thread = threading.Thread( target=self._send )
			self._send_thread.daemon = True
			self._send_thread.start()


	def _listen(self):
		log.debug("Begin executing NodeProxy listen thread")
		while True:
			if self.txsocket.poll( self.timeout, zmq.POLLIN ):
				data = self.txsocket.recv_serialized( self._deserialize )
				self.txbuffer.put( data )


	def _deserialize(self, zmq_frames):
		frame = zmq_frames[0]
		num_c64 = len(frame) // 8
		flatdata = np.array(struct.unpack("ff"*num_c64, frame), dtype=np.complex64)
		complex_data = flatdata[::2] + 1j*flatdata[1::2]
		return complex_data


	def _send(self):
		log.debug("Begin executing NodeProxy send thread")
		while True:
			try:
				data = self.rxbuffer.get( self.timeout/1e3 )
			except queue.Empty:
				continue
			self.rxsocket.send( data )
			self.rxbuffer.task_done()
