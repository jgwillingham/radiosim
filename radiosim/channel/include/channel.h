#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <zmq.hpp>
#include "node_proxy.h"

#ifndef _CHANNEL_INCLUDED_
#define _CHANNEL_INCLUDED_

class Channel {
	public:
		Channel();
		~Channel();

		void add_node(unsigned int txport, unsigned int rxport, int buffer_size);
		void start();
		
	private:
		void run_main_loop();
		std::thread loop_thread;
		std::atomic<bool> channel_is_on;

		std::vector<NodeProxy*> nodes;
		zmq::context_t ctx;
};


extern "C"{
	Channel* channel_new(){return new Channel;}
	void channel_add_node(Channel* channel, unsigned int txport, unsigned int rxport, int buffer_size){
		channel->add_node(txport, rxport, buffer_size);
	}
	void channel_start(Channel* channel){channel->start();}
}

#endif
