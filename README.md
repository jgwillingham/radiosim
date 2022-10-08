# RadioSim
RadioSim is a simulation tool for RF digital communications written in Python and C++. 

The aim of this project is to develop a wireless network simulator that is lightweight but still powerful enough for basic proof-of-concept testing of cognitive radio applications. Much of RadioSim is a thin Python wrapper over highly multithreaded C++ code (thereby side-stepping limitations imposed by the GIL to improve performance). With the basic objects provided by the Python interface, cognitive engines can easily be written in Python and simulated.

<h1 align="center">
 <img src="/extra/radiosim.drawio.svg" width="320">
</h1><br>


### Overview
The systems simulated by RadioSim can be broken down into 3 major parts: the transmitter (TX), the receiver (RX), and the channel. The data sent by the transmitter are corrupted by noise in the channel and the task of the receiver is to recover the data from the corrupted signal. The implementation of these parts is in `Transmitter`, `Receiver`, and `Channel` classes. In general, there can be many transmitters and receivers working at the same time whereas there will typically only be a single `Channel` object.

For a single `Transmitter` and `Receiver`, the signal chain looks like this:

`DataSource`  &LongRightArrow;  `Transmitter`  &LongRightArrow;  `Channel`  &LongRightArrow;  `Receiver`  &LongRightArrow;  `DataSink`

Each "&LongRightArrow;" in this chain indicates data being passed via socket interfaces. So a `DataSource` takes the data to be sent and sources it to the `Transmitter` in chunks for coding, modulation, and upconversion. Then the `Transmitter` passes the complex passband data to the `Channel` where in general it would be distorted based on some channel model and then distributed to all `Receiver` objects in the network. The `Receiver` receives the distorted signal on its listening socket, downconverts and demodulates the signal and then finally passes the received bytes to a DataSink which processes them.

The `Transmitter` and `Receiver` objects both require information about how they should modulate/demodulate data. To get this information, they must be given a modem (i.e. a child class of the abstract base `Modem`). Several standard modulation schemes are provided as prebuilt modem classes (BPSK, QPSK), but it is easy to construct a custom modem if desired.

### Tests
To run tests with pytest: run `pytest` from the root directory. To run tests with unittests, run `python3 -m unittest discover` from the root directory.
