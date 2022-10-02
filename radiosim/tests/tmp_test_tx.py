from transceiver import Transmitter
from transceiver import Receiver
from data_source_sink import DataSource
from modems import BPSKModem, QPSKModem 
import argparse
import time
import numpy as np
import struct
import queue
import logging
log = logging.getLogger(__name__)

from matplotlib import pyplot as plt

def get_tx(sps, **params):
	qpsk = QPSKModem(sps=sps)
	qpsk.center_freq = 0
	tx = Transmitter(qpsk, **params)
	return tx


def get_rx(sps, **params):
	qpsk = QPSKModem(sps=sps)
	qpsk.center_freq = 0
	rx = Receiver(qpsk, **params)
	return rx


def watch_back_buffer(rx):
	rx_bytes = []
	nbytes = 0
	while True:
		try:
			rawdata = rx.buf_back.get( timeout=1 )
		except queue.Empty:
			log.warning("Receiver timeout")
			break
		log.debug(f"Received {len(rawdata)} bytes")
		nbytes += len(rawdata)
		rx_bytes.append(rawdata)
	databytes = b''
	for byts in rx_bytes: databytes += byts
	num_uint8s = nbytes #// 8
	rx_data = struct.unpack("B"*num_uint8s, databytes)
	return rx_data
		


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--nchunks", type=int, default=5)
	parser.add_argument("-s", "--sps", type=int, default=8)
	parser.add_argument("-p", "--plot-data", action='store_true', default=False)
	parser.add_argument("-l", "--log", type=str, default="info")
	args = parser.parse_args()
	return args


if __name__=="__main__":
	args = parse_args()
	nchunks = args.nchunks
	sps = args.sps
	plot_data = args.plot_data
	loglevel = getattr(logging, args.log.upper(), None)	
	logging.basicConfig(level=loglevel, format="{levelname} | {threadName} | {module} :: {message}", style="{")

	# Start Receiver
	rx = get_rx(sps=sps, iport=22222)
	rx.start()

	time.sleep(1)

	# Start Transmitter
	tx = get_tx(sps=sps, iport=11111, oport=22222)
	tx.start()

	time.sleep(1)
	print("")

	# Start sourcing random data to TX
	data = (100*np.random.rand(512*nchunks-1)).astype(np.uint8)
	src = DataSource(data, oport=11111)
	src.start()

	# Watch RX back buffer for the demodulated data
	rx_data = watch_back_buffer(rx)

	# stop TX and RX
	tx.stop()
	src.join(0)
	rx.stop()

	# Compare received data to original data
	results = rx_data == data
	error = 1 - sum(results)/len(results)
	log.info(f"Data transfer complete. ERROR = {error*100}%\n")

	if plot_data:
		plt.plot(rx_data)
		plt.show()
