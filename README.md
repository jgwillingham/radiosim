# RadioSim

RadioSim is a simulation tool for RF digital communications written in Python. 

### Overview
The systems simulated by RadioSim can be broken down into 3 major parts: the transmitter (TX), the receiver (RX), and the channel. The data sent by the transmitter are corrupted by noise in the channel and the task of the receiver is to recover the data from the corrupted signal. The implementation of these parts is in `Transmitter`, `Receiver`, and `Channel` objects. In general, there can be many transmitters and receivers working at the same time whereas there will typically only be a single `Channel` object.

For a single `Receiver` and `Transmitter`, the signal chain looks like this:

`DataSource` &rarr `Transmitter` &rarr `Channel` &rarr `Receiver` &rarr `DataSink`

Each &rarr in this chain indicates data being passed via socket interfaces. So a `DataSource` object takes the data to be sent and sources it to the `Transmitter` in chunks for coding, modulation, and upconversion. Then the `Transmitter` passes the complex passband data to the `Channel` where in general it would be distorted based on some channel model and then distributed to all `Receiver` objects in the network. The `Receiver` receives the distorted signal on its listening socket, downconverts and demodulates the signal and then finally passes the received bytes to a DataSink which processes them.


### Tests
To run tests with pytest: run `pytest` from the root directory. To run tests with unittests, run `python3 -m unittest discover` from the root directory.
