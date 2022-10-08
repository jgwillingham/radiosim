from radiosim.transceiver import Transmitter, Receiver
from radiosim.channel import Channel
from radiosim.data_source_sink import DataSource
from radiosim.modems import BPSKModem, QPSKModem 
import argparse
import time
import numpy as np
import struct
import queue
import logging
log = logging.getLogger(__name__)


SUPPORTED_DTYPES = ["uint8", "float32", "float64"]
SUPPORTED_MODULATIONS = ["bpsk", "qpsk"]


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n",
			"--num-nodes",
			type=int,
			default=1)
	parser.add_argument("-c", 
			"--nchunks", 
			type=int, 
			default=10)
	parser.add_argument("-s", 
			"--sps", 
			type=int, 
			default=8)
	parser.add_argument("-l", 
			"--log", 
			type=str, 
			default="warning")
	parser.add_argument("-d", 
			"--dtype", 
			type=str, 
			default="uint8", 
			choices=SUPPORTED_DTYPES)
	parser.add_argument("-f", 
			"--freq", 
			type=float, 
			default=2.4e9)
	parser.add_argument("-m", 
			"--modulation", 
			type=str, 
			default="qpsk", 
			choices=SUPPORTED_MODULATIONS)
	parser.add_argument("-v",
			"--verbose",
			action="store_true",
			default=False)
	args = parser.parse_args()
	return args


def watch_back_buffer(rx, dtype, dlen):
	rx_bytes = []
	nbytes = 0
	while nbytes < dlen:
		try:
			rawdata = rx.buf_back.get( timeout=1 )
		except queue.Empty:
			continue
		log.debug(f"Received {len(rawdata)} bytes")
		nbytes += len(rawdata)
		rx_bytes.append(rawdata)
	print(f"Received all {dlen} bytes of data")
	databytes = b''
	for byts in rx_bytes: databytes += byts
	if dtype == np.uint8:
		num_uint8s = nbytes
		rx_data = struct.unpack("B"*num_uint8s, databytes)
	elif dtype == np.float32:
		num_float32s = nbytes // 4
		rx_data = struct.unpack("f"*num_float32s, databytes)
	elif dtype == np.float64:
		num_float64s = nbytes // 8
		rx_data = struct.unpack("d"*num_float64s, databytes)

	return rx_data
		



if __name__=="__main__":
	args = parse_args()
	num_nodes = args.num_nodes
	nchunks = args.nchunks
	sps = args.sps
	datatype = eval(f"np.{args.dtype.lower()}")
	freq = args.freq
	modulation = args.modulation.lower()
	verbose = args.verbose
	loglevel = getattr(logging, args.log.upper(), None)

	if verbose:
		logging.basicConfig(level=loglevel, format="{levelname} | {threadName} | {module} :: {message}", style="{")
	else:
		logging.basicConfig(level=loglevel, format="{levelname} :: {message}", style="{")
		
	print(f"Modem configured for {modulation.upper()} at {freq/1e9} GHz")
	if modulation == "qpsk":
		modem = QPSKModem
	elif modulation == "bpsk":
		modem = BPSKModem

	data = (100*np.random.rand(512*nchunks-1)).astype(datatype)
	dlen = len(bytearray(data))

	ch = Channel()

	nodes = []
	for i in range(num_nodes):
		txport = 22222+i
		rxport = 33333+i
		srcport= 11111+i
		mdm = modem(sps=sps)
		mdm.center_freq = freq + i*10e6
		rx = Receiver(mdm, iport=rxport)
		tx = Transmitter(mdm, iport=srcport, oport=txport) 
		src = DataSource(data, oport=srcport)
		ch.add_node(txport, rxport, 512)
		nodes.append( (rx,tx,src) )

	for node in nodes: node[0].start()
	time.sleep(1)
	for node in nodes: node[1].start()
	ch.start()
	for node in nodes: node[2].start()

	# Watch RX back buffer for the demodulated data
	rx1_data = watch_back_buffer(nodes[0][0], datatype, dlen)
	#rx2_data = watch_back_buffer(rx2, datatype, dlen)

	# stop TX and RX
	for node in nodes: node[0].stop()
	for node in nodes: node[1].stop()
	for node in nodes: node[2].join(0)

	# Compare received data to original data
	results = rx1_data == data
	error = 1 - sum(results)/len(results)
	print(f"Data transfer complete. ERROR = {error*100:.2f}%")
