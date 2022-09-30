# RadioSim

RadioSim is a simulation tool for digital communications written in Python and C++.

### Overview
The systems simulated by RadioSim can be broken down into 3 major parts: the transmitter (TX), the receiver (RX), and the channel. The data sent by the transmitter are corrupted by noise in the channel and the task of the receiver is to recover the data from the corrupted signal.

In RadioSim, the transmitter, receiver, and channel are all simulated as independent processes which pass data via socket interfaces. The transmitter and receiver each consist of several parts which then each run in their own thread.

### Tests
To run tests, from the root directory, run `./run_tests` or equivalently `python3 -m unittest discover`.
