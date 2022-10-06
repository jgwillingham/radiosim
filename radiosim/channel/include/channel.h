#include <iostream>
#include <vector>
#include <zmq.hpp>
#include "node_proxy.h"

#ifndef _CHANNEL_INCLUDED_
#define _CHANNEL_INCLUDED_

class Channel {
	public:
		Channel();
		~Channel();

		void add_node(short txport, short rxport, int buffer_size);
		void start();
		
	private:
		void run_main_loop();
		std::vector<NodeProxy*> nodes;
		zmq::context_t ctx;
};

#endif
