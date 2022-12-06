
#ifndef NODEPROXY_INCLUDED
#define NODEPROXY_INCLUDED

#include <iostream>
#include <thread>
#include <atomic>
#include <zmq.hpp>
#include "common.h"
#include "threadsafe_queue.h"
#include "ring_buffer.h"


class NodeProxy {
	public:
		//constructor
		NodeProxy(zmq::context_t& ctx, unsigned int txport, unsigned int rxport, size_t buffer_size);
		//destructor
		~NodeProxy();
		//copy constructor
		NodeProxy(const NodeProxy&) = default;
		//assignment (member-wise) constructor
		NodeProxy& operator=(const NodeProxy&) = default;
		//move constructor
		NodeProxy(NodeProxy&&) = default;

		void start();

		unsigned int txport;
		unsigned int rxport;
		threadsafe_queue<vector_c64> txbuffer;
		threadsafe_queue<vector_c64> rxbuffer;
	private:
		void init_sockets(zmq::context_t& ctx, unsigned int txport, unsigned int rxport);

		void txlisten();
		void rxsend();

		std::thread txlisten_thread;
		std::thread rxsend_thread;
		std::atomic<bool> tx_is_active;
		std::atomic<bool> rx_is_active;

		vector_c64 unpack_to_complex64(zmq::message_t& msg);
		zmq::message_t pack_complex64_to_message(vector_c64& complexdata);

		zmq::socket_t txsocket;
		zmq::socket_t rxsocket;
};


#endif
