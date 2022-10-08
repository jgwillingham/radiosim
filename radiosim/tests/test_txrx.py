import unittest
from radiosim.transceiver import Transmitter, Receiver
from radiosim.data_source_sink import DataSource
from radiosim.modems import QPSKModem 
import time
import numpy as np
import struct
import queue
import threading
import zmq


class TxRxTesting(unittest.TestCase):
	def test_transmit_recv(self):
		"""
		Test directly sending modulated passband data
		from Transmitter to Receiver. Test recv data == true data
		"""
		modem = QPSKModem()
		modem.center_freq = 1e6

		self.rx = Receiver(modem, iport=33333)
		self.tx = Transmitter(modem, iport=11111, oport=22222)

		self.finished = False

		data = np.random.rand(1000).astype(np.float64)
		self.dlen = len(bytearray(data))
		src = DataSource(data=data, oport=11111)

		self.rx.start()
		time.sleep(0.5)
		self.tx.start()
		time.sleep(0.5)
		self.run_middleman(22222, 33333)
		src.start()

		print("Watching Rx back buffer...")
		rx_data = self.watch_back_buffer()
		print("Received all data")
		self.tx.stop()
		src.join(0)
		self.rx.stop()

		self.assertTrue( np.all(rx_data == data) )


	def watch_back_buffer(self):
		rx_bytes = b''
		nbytes = 0
		while nbytes < self.dlen:
			try:
				rawdata = self.rx.buf_back.get( timeout=5 )
			except queue.Empty:
				return
			nbytes += len(rawdata)
			rx_bytes += rawdata
		self.finished = True
		num_float64s = nbytes // 8
		rx_data = struct.unpack("d"*num_float64s, rx_bytes)
		return rx_data


	def run_middleman(self, txport, rxport):
		mm_thread = threading.Thread( target=self._middleman, args=(txport, rxport) )
		mm_thread.daemon = True
		mm_thread.start()


	def _middleman(self, txport, rxport):
		ctx = zmq.Context()
		txsock = ctx.socket(zmq.PULL)
		txsock.bind(f"tcp://127.0.0.1:{txport}")
		rxsock = ctx.socket(zmq.PUSH)
		rxsock.bind(f"tcp://127.0.0.1:{rxport}")
		
		while not self.finished:
			data = txsock.recv()
			rxsock.send(data)
		txsock.close()
		rxsock.close()
		

