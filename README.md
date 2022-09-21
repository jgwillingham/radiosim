# RadioSim

RadioSim is a simulation tool for digital communications written in Python and C++.

### Overview
The systems simulated by RadioSim can be broken down into 3 major parts: the transmitter (TX), the receiver (RX), and the channel. The data sent by the transmitter are corrupted by noise in the channel and the task of the receiver is to recover the data from the corrupted signal. The signal path looks like:

|------------------------TX--------------------------|------channel------|-------------------------RX--------------------------|
|digital source| --> |channel encoder| --> |modulator| --> |channel| --> |demodulator| --> |channel decoder| --> |received data|

In RadioSim, the transmitter, receiver, and channel are all simulated as independent processes which pass data via socket interfaces. The transmitter and receiver each consist of several parts which then each run in their own thread.

### Tests
To run tests, from the root directory, run

`python3 -m unittest discover`
