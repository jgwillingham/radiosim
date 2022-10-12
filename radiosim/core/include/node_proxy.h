#include <iostream>
#include <queue>
#include <thread>
#include <atomic>
#include <mutex>
#include <string>
#include <zmq.hpp>

#ifndef _NODEPROXY_INCLUDED_
#define _NODEPROXY_INCLUDED_

#include "common.h"
#include "atomic_queue.h"


class NodeProxy {
	public:
		NodeProxy(zmq::context_t& ctx, unsigned int txport, unsigned int rxport, int buffer_size);
		~NodeProxy();

		void start();

		unsigned int txport;
		unsigned int rxport;
		atomic_queue<vector_c64> txbuffer;
		atomic_queue<vector_c64> rxbuffer;
	private:
		void init_sockets(zmq::context_t& ctx, unsigned int txport, unsigned int rxport);
		void init_buffers(int buffer_size);

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
