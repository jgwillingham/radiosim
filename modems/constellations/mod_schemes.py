"""
Symbol mappings for common modulation schemes
"""
from .constellation import Constellation


bpsk_map = {
	0b0 : -1,
	0b1 : 1}
BPSKConstellation = Constellation( bpsk_map )


qpsk_map = {
	0b00 : -1 - 1j,
	0b01 : -1 + 1j,
	0b10 :  1 - 1j,
	0b11 :  1 + 1j}
QPSKConstellation = Constellation( qpsk_map )
