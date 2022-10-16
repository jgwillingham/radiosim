import unittest
import numpy as np
import struct
from radiosim.node.modems import QPSKModem
from radiosim.node.modems.utils.ofdm import OFDM


class OFDMTesting(unittest.TestCase):
	qpsk = QPSKModem()
	ofdm = OFDM(ncarriers=64, non=52)
	def test_moddemod(self):
		npoints = 52*10
		test_data = np.random.rand(npoints)*255
		symbols = self.qpsk.map(test_data)
		ofdm_time = self.ofdm.ofdm_modulate(symbols)

		approx_syms = self.ofdm.ofdm_demodulate(ofdm_time)
		rx_symbols = self.qpsk.get_euclidean_estimates(approx_syms)
		rx_bytes = self.qpsk.demap(rx_symbols)
		rx_data = struct.unpack("d"*npoints, rx_bytes)

		self.assertTrue( np.all(rx_data == test_data) )
		

if __name__=="__main__":
	unittest.main()
