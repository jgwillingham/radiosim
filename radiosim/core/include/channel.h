
#ifndef CHANNEL_INCLUDED
#define CHANNEL_INCLUDED

#include <iostream>
#include <thread>
#include <atomic>
#include <random>
#include <zmq.hpp>
#include "common.h"
#include "node_proxy.h"


class Channel {
	public:
		Channel(float noise_energy);
		~Channel();

		void add_node(unsigned int txport, unsigned int rxport, int buffer_size);
		void start();
		
	private:
		void run_main_loop();
		std::thread loop_thread;
		std::atomic<bool> channel_is_on;

		std::vector<NodeProxy*> nodes;
		zmq::context_t ctx;

		std::normal_distribution<float> normal;
		std::default_random_engine randgen;

		vector_c64 generate_complex_awgn(size_t nsamples);
};


// for Python ctypes wrapper
extern "C"{
	Channel* channel_new(float noise_energy){return new Channel(noise_energy);}
	void channel_add_node(Channel* channel, unsigned int txport, unsigned int rxport, int buffer_size){
		channel->add_node(txport, rxport, buffer_size);
	}
	void channel_start(Channel* channel){channel->start();}
}

#endif
