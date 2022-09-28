from transceiver import Transmitter
from data_source_sink import DataSource
from modems import QPSKModem 
import argparse
import time
import zmq
import numpy as np
import struct
import logging
log = logging.getLogger(__name__)


def get_tx(sps):
	qpsk = QPSKModem(sps=sps)
	qpsk.center_freq = 0
	tx = Transmitter(qpsk)
	return tx


def start_data_source(nchunks):
	data = np.arange(512*nchunks-1, dtype=np.uint8)
	src = DataSource(data)
	src.start()


def receive():
	cont = zmq.Context()
	rx_socket = cont.socket(zmq.PULL)
	rx_socket.connect("tcp://127.0.0.1:22222")
	iq = np.array([])
	for _ in range(nchunks):
		rawdata = rx_socket.recv()
		nbytes = len(rawdata)
		nsamples = nbytes // 16 # assuming complex doubles
		log.info( f"Received {nbytes} bytes = {nsamples} complex samples" )
		data = struct.unpack("dd"*nsamples, rawdata)
		data = np.array(data)
		iq = np.append(iq, data[::2] + 1j*data[1::2] )
	return iq


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--chunksize", type=int, default=5)
	parser.add_argument("-s", "--sps", type=int, default=4)
	parser.add_argument("-p", "--print-data", action='store_true', default=False)
	args = parser.parse_args()
	return args


if __name__=="__main__":
	args = parse_args()
	nchunks = args.chunksize
	sps = args.sps
	print_data = args.print_data
	
	
	logging.basicConfig(level=logging.DEBUG, format="{levelname}: [{threadName} | {name}] <> {message}", style="{")

	tx = get_tx(sps=sps)
	tx.start()
	print("")
	time.sleep(1)
	start_data_source(nchunks)

	iq = receive()
	tx.stop()
	if print_data:
		print(iq)
