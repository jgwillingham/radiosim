import numpy as np


class OFDM:
	"""
	Class for OFDM (Orthogonal Frequency-Division Multiplexing) waveform
	modulation and demodulation
	"""
	def __init__(self, ncarriers, non, cplen=None):
		self.ncarriers = ncarriers
		self.non = non

		idx_on = np.arange(-non//2, non//2)
		idx_on[non//2:] += 1
		self.idx_on = idx_on

		if cplen is None: cplen = ncarriers // 4
		self.cplen = cplen


	def ofdm_modulate(self, symbols):
		frames = self.pack_frames(symbols)
		frames_cp = self.add_cyclic_prefix(frames)
		ofdm_time = np.hstack(frames_cp)
		return ofdm_time


	def ofdm_demodulate(self, ofdm_time):
		frames = self.remove_cyclic_prefix(ofdm_time)
		approx_symbols = self.unpack_frames(frames)
		return approx_symbols


	def pack_frames(self, symbols):
		parallel = [symbols[i*self.non:(i+1)*self.non] for i in range(len(symbols)//self.non)]

		frames = []
		for par in parallel:
			frame = np.zeros(self.ncarriers, dtype=np.complex64)
			frame[self.idx_on] = np.array(par)
			frame = np.fft.ifft(frame)
			frames.append(frame)

		if len(symbols) % self.non != 0:
			leftover = symbols[len(parallel)*self.non:]
			frame = np.zeros(self.ncarriers, dtype=np.complex64)
			frame[self.idx_on[:len(leftover)]] = leftover
			frame = np.fft.ifft(frame)
			frames.append(frame)
	
		return frames


	def unpack_frames(self, ofdm_frames):
		carriervalues = [np.fft.fft(frame) for frame in ofdm_frames]
		approx_symbols = np.array([frame[self.idx_on] for frame in carriervalues]).flatten()
		return approx_symbols


	def add_cyclic_prefix(self, frames):
		frames_cp = frames[:]
		for i, frame in enumerate(frames):
			prefix = frame[-self.cplen:]
			frames_cp[i] = np.hstack([prefix, frame])
		return frames_cp


	def remove_cyclic_prefix(self, ofdm_time):
		framesize = self.cplen + self.ncarriers
		nframes = len(ofdm_time) // framesize
		frames = [ofdm_time[i*framesize : (i+1)*framesize][self.cplen:] for i in range(nframes)]
		return frames


