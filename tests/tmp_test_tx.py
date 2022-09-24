from transceiver import Transmitter
from data_source_sink import DataSource
from modems import QPSKModem 
import time
import zmq
import numpy as np
import struct
from matplotlib import pyplot as plt
import logging
log = logging.getLogger(__name__)

if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG, format="{levelname}: [{threadName} | {name}] <> {message}", style="{")
	qpsk = QPSKModem(sps=8)
	qpsk.center_freq = 0
	tx = Transmitter(qpsk)
	tx.start()

	time.sleep(1)

	data = np.arange(10, dtype=np.uint8)
	src = DataSource(data)
	src.start()
	
	cont = zmq.Context()
	rx_socket = cont.socket(zmq.PULL)
	rx_socket.connect("tcp://127.0.0.1:22222")
	for _ in range(1):
		rawdata = rx_socket.recv()
		nbytes = len(rawdata)
		nsamples = nbytes // 16 # assuming complex doubles
		log.info( f"Received {nbytes} bytes = {nsamples} complex samples" )
		#data = struct.unpack("dd"*nsamples, rawdata)
		#data = np.array(data)
		#iq = data[::2] + 1j*data[1::2]
	tx.stop()
