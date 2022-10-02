from radiosim.transceiver import Transmitter, Receiver
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
		modem = QPSKModem(sps=sps)
	elif modulation == "bpsk":
		modem = BPSKModem(sps=sps)
	modem.center_freq = freq

	# Start Receiver
	rx = Receiver(modem, iport=22222)
	rx.start()

	time.sleep(1)

	# Start Transmitter
	tx = Transmitter(modem, iport=11111, oport=22222)
	tx.start()

	time.sleep(1)

	# Start sourcing random data to TX
	data = (100*np.random.rand(512*nchunks-1)).astype(datatype)
	dlen = len(bytearray(data))
	src = DataSource(data, oport=11111)
	print(f"Sourcing {dlen} bytes of {args.dtype} data to transmitter")
	src.start()
	print("Transmitting...")
	# Watch RX back buffer for the demodulated data
	rx_data = watch_back_buffer(rx, datatype, dlen)


	# stop TX and RX
	tx.stop()
	src.join(0)
	rx.stop()

	# Compare received data to original data
	results = rx_data == data
	error = 1 - sum(results)/len(results)
	print(f"Data transfer complete. ERROR = {error*100}%")
