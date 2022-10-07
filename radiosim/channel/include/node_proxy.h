#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <complex>
#include <zmq.hpp>

#ifndef _NODEPROXY_INCLUDED_
#define _NODEPROXY_INCLUDED_

typedef std::vector<std::complex<float>> vector_c64;

class NodeProxy {
	public:
		NodeProxy(zmq::context_t &ctx, short txport, short rxport, int buffer_size);
		~NodeProxy(){};

		void start();

		short txport;
		short rxport;
		std::queue<vector_c64> txbuffer;
		std::queue<vector_c64> rxbuffer;
	private:
		void init_sockets(zmq::context_t &ctx, short txport, short rxport);
		void init_buffers(int buffer_size);
		void txlisten();
		vector_c64 unpack_to_complex64(std::string msg_str);

		zmq::socket_t txsocket;
		zmq::socket_t rxsocket;
};


#endif
