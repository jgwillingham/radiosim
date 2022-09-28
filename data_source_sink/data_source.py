import zmq
import threading
import logging
log = logging.getLogger(__name__)


class DataSource(threading.Thread):
	def __init__(self, data, oport=11111, chunksize=512):
		super().__init__()
		self.serial_data = data
		self.chunksize = chunksize
		self.initialize_socket( oport )


	def initialize_socket(self, oport):
		self.target_port = oport
		self.zmq_context = zmq.Context()
		self.output_socket = self.zmq_context.socket( zmq.PUSH )
		self.output_socket.connect( f"tcp://127.0.0.1:{oport}" )


	def run(self):
		log.info("Starting data source thread")
		chunk = self.chunksize
		curr_idx = 0
		finished = False
		while not finished:
			if curr_idx + self.chunksize > len(self.serial_data):
				chunk = len(self.serial_data) - curr_idx + 1
				finished = True
			data_chunk = self.serial_data[curr_idx:curr_idx + chunk]
			self.output_socket.send( data_chunk )
			curr_idx += chunk
