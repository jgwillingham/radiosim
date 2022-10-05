#include <iostream>
#include <vector>
#include <zmq.hpp>

#ifndef _NODEPROXY_INCLUDED_
#define _NODEPROXY_INCLUDED_

class NodeProxy {
	public:
		NodeProxy(zmq::context_t* p_ctx, short txport, short rxport, int buffer_size);
		~NodeProxy(){};

		void start();

		short txport;
		short rxport;
		std::vector<float> txbuffer;
		std::vector<float> rxbuffer;
	private:
		void init_sockets(zmq::context_t* p_ctx, short txport, short rxport);
		void init_buffers(int buffer_size);
		void txlisten();

		zmq::socket_t txsocket;
		zmq::socket_t rxsocket;
};


#endif
