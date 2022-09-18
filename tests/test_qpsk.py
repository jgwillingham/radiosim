import unittest
from modems import QPSKModem
import numpy as np

class QPSKTesting(unittest.TestCase):
	qpsk = QPSKModem()
	def test_make_words_range(self):
		"""
		TEST: 2-bit words have values in range 0-3
		Generate random array of 100 floats and create
		2-bit words. Assert they are all in correct range.
		"""
		test_data = np.random.rand(100)
		words = self.qpsk.make_words(test_data)
		self.assertTrue( np.all(words <= 3) and np.all(0 <= words) )

	def test_make_words_value(self):
		"""
		TEST: Input data produces correct words
		Use input data = [27, 228]
		- 27 as uint8 is 00011011 -> 00 01 10 11 -> 0 1 2 3
		-228 as uint8 is 11100100 -> 11 10 01 00 -> 3 2 1 0
		"""
		test_data = np.array([27, 228], dtype=np.uint8)
		true_words = np.array([0, 1, 2, 3, 3, 2, 1, 0], dtype=np.uint8)
		words = self.qpsk.make_words(test_data)
		self.assertTrue( np.all(words == true_words) )

	def test_map(self):
		"""
		TEST: Input data is correctly mapped to complex symbols
		"""
		test_data = np.array([27, 228], dtype=np.uint8)
		true_symbols = np.array([-1-1j, -1+1j, 1-1j, 1+1j, 1+1j, 1-1j, -1+1j, -1-1j])
		symbols = self.qpsk.map(test_data)
		self.assertTrue( np.all(symbols == true_symbols) )


if __name__ == "__main__":
	unittest.main()
