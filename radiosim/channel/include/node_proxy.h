#include <iostream>
#include <vector>
#include <string>
#include <complex>
#include <zmq.hpp>

#ifndef _NODEPROXY_INCLUDED_
#define _NODEPROXY_INCLUDED_

class NodeProxy {
	public:
		NodeProxy(zmq::context_t &ctx, short txport, short rxport, int buffer_size);
		~NodeProxy(){};

		void start();

		short txport;
		short rxport;
		std::vector< std::vector<std::complex<float>> > txbuffer;
		std::vector< std::vector<std::complex<float>> > rxbuffer;
	private:
		void init_sockets(zmq::context_t &ctx, short txport, short rxport);
		void init_buffers(int buffer_size);
		void txlisten();
		std::vector<std::complex<float>> unpack_to_complex64(std::string msg);

		zmq::socket_t txsocket;
		zmq::socket_t rxsocket;
};


#endif
