#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <zmq.hpp>
#include <channel.h>

// Constructor
Channel::Channel(float noise_energy) : normal{0.0, noise_energy} {};


// Destructor
Channel::~Channel(){
	channel_is_on.store(false);
	if (loop_thread.joinable()){
		loop_thread.join();
	}
	ctx.shutdown();
	ctx.close();
	int num_nodes = nodes.size();
	for (int i=0; i<num_nodes; i++){
		delete nodes[i];
	}
};


// Add a new node to the channel network
void Channel::add_node(unsigned int txport, unsigned int rxport, int buffer_size){
	NodeProxy* new_node = new NodeProxy(ctx, txport, rxport, buffer_size);
	nodes.push_back( new_node );
}


// Start the channel
void Channel::start(){
	for (auto& node : nodes ){
		node->start();
	}
	channel_is_on.store(true);
	loop_thread = std::thread(&Channel::run_main_loop, this);
}


// Runs the main loop of the channel - reading from buffers, processing, and writing to buffers
void Channel::run_main_loop(){
	vector_c64 data;
	data.reserve(512);
	while ( channel_is_on.load() ){
		std::this_thread::sleep_for( std::chrono::milliseconds(100) );
		for (auto& node : nodes){
			if (not node->txbuffer.empty()){
				data = node->txbuffer.front();
				node->txbuffer.pop();
				vector_c64 noise = generate_complex_awgn(data.size());
				data = data + noise;
				node->rxbuffer.push( data );
			}
		}
	}
}



// Generate nsamples of complex additive white gaussian noise
vector_c64 Channel::generate_complex_awgn(size_t nsamples){
	vector_c64 noise(nsamples);
	for (int i=0; i<nsamples; i++){
		noise[i] = std::complex<float>(normal(randgen), normal(randgen));
	}
	return noise;
}
