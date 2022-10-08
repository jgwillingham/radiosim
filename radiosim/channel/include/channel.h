#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <random>
#include <algorithm>
#include <zmq.hpp>
#include "node_proxy.h"

#ifndef _CHANNEL_INCLUDED_
#define _CHANNEL_INCLUDED_

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


// overload + operator to sum complex vectors elementwise
vector_c64 operator+(const vector_c64& vec1, const vector_c64& vec2){
	assert(vec1.size() == vec2.size());
	size_t dim = vec1.size();
	vector_c64 vsum(dim);
	std::transform(vec1.begin(), vec1.end(), vec2.begin(), vsum.begin(), std::plus<std::complex<float>>());
	return vsum;
}



// for Python ctypes wrapper
extern "C"{
	Channel* channel_new(float noise_energy){return new Channel(noise_energy);}
	void channel_add_node(Channel* channel, unsigned int txport, unsigned int rxport, int buffer_size){
		channel->add_node(txport, rxport, buffer_size);
	}
	void channel_start(Channel* channel){channel->start();}
}

#endif
