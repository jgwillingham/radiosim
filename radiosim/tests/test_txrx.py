import unittest
from radiosim.transceiver import Transmitter, Receiver
from radiosim.data_source_sink import DataSource
from radiosim.modems import QPSKModem 
import time
import numpy as np
import struct
import queue


class TxRxTesting(unittest.TestCase):
	def test_transmit_recv(self):
		"""
		Test directly sending modulated passband data
		from Transmitter to Receiver. Test recv data == true data
		"""
		modem = QPSKModem()
		modem.center_freq = 1e6

		self.rx = Receiver(modem, iport=22222)

		self.tx = Transmitter(modem, iport=11111, oport=22222)

		data = np.random.rand(1000).astype(np.float64)
		self.dlen = len(bytearray(data))
		src = DataSource(data=data, oport=11111)

		self.rx.start()
		time.sleep(0.5)
		self.tx.start()
		time.sleep(0.5)
		src.start()

		rx_data = self.watch_back_buffer()

		self.tx.stop()
		src.join(0)
		self.rx.stop()

		self.assertTrue( np.all(rx_data == data) )


	def watch_back_buffer(self):
		rx_bytes = []
		nbytes = 0
		while nbytes < self.dlen:
			try:
				rawdata = self.rx.buf_back.get( timeout=5 )
			except queue.Empty:
				return
			nbytes += len(rawdata)
			rx_bytes.append(rawdata)
		databytes = b''
		for byts in rx_bytes: databytes += byts
		num_float64s = nbytes // 8
		rx_data = struct.unpack("d"*num_float64s, databytes)
		return rx_data
		

