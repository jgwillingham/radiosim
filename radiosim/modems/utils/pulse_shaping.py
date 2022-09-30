import numpy as np
import sys


DEFAULT_SPS = 4

	
def rrc_filter(sps=DEFAULT_SPS, num_positive_lobes=4, alpha=0.33):
    """
    Root raised cosine (RRC) filter (FIR) impulse response.

    sps: number of samples per symbol

    num_positive_lobes: number of positive overlaping symbols
    length of filter is 2 * num_positive_lobes + 1 samples

    alpha: roll-off factor
    """

    N = sps * (num_positive_lobes * 2 + 1)
    t = (np.arange(N) - N / 2) / sps

    # result vector
    h_rrc = np.zeros(t.size, dtype=float)

    # index for special cases
    sample_i = np.zeros(t.size, dtype=bool)

    # deal with special cases
    subi = t == 0
    sample_i = np.bitwise_or(sample_i, subi)
    h_rrc[subi] = 1.0 - alpha + (4 * alpha / np.pi)

    subi = np.abs(t) == 1 / (4 * alpha)
    sample_i = np.bitwise_or(sample_i, subi)
    h_rrc[subi] = (alpha / np.sqrt(2)) \
		* (((1 + 2 / np.pi) * (np.sin(np.pi / (4 * alpha))))
		+ ((1 - 2 / np.pi) * (np.cos(np.pi / (4 * alpha)))))

    # base case
    sample_i = np.bitwise_not(sample_i)
    ti = t[sample_i]
    h_rrc[sample_i] = np.sin(np.pi * ti * (1 - alpha)) \
		    + 4 * alpha * ti * np.cos(np.pi * ti * (1 + alpha))
    h_rrc[sample_i] /= (np.pi * ti * (1 - (4 * alpha * ti) ** 2))

    return h_rrc


	
def _get_supported_pulse_shapes():
	this_module = sys.modules[__name__]
	supported_pulse_shapes = [fn for fn in dir(this_module) \
					if not fn.startswith("_") and fn not in ["np", "sys"]]
	supported_pulse_shapes.extend([ps.split('_filter')[0] for ps in supported_pulse_shapes if '_filter' in ps])
	return supported_pulse_shapes

SUPPORTED_PULSE_SHAPES = _get_supported_pulse_shapes()	
