#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <zmq.hpp>
#include <channel.h>

// Constructor
Channel::Channel(){};


// Destructor
Channel::~Channel(){
	ctx.shutdown();
	ctx.close();
	int num_nodes = nodes.size();
	for (int i=0; i<num_nodes; i++){
		delete nodes[i];
	}
};


// Add a new node to the channel network
void Channel::add_node(short txport, short rxport, int buffer_size){
	NodeProxy* new_node = new NodeProxy(ctx, txport, rxport, buffer_size);
	nodes.push_back( new_node );
	std::cout << "Added new node to channel network" << std::endl;
}


// Start the channel
void Channel::start(){
	int num_nodes = nodes.size();
	for (int i=0; i<num_nodes; i++ ){
		std::cout << "Starting node " << i << std::endl;
		nodes[i]->start();
	}
	run_main_loop();
}


// Runs the main loop of the channel - reading from buffers, processing, and writing to buffers
void Channel::run_main_loop(){
	vector_c64 data;
	data.reserve(512);
	while (true){
		std::this_thread::sleep_for( std::chrono::milliseconds(100) );
		for (auto& node : nodes){
			if (not node->txbuffer.empty()){
				std::cout << "Found data in buffer: ";
				data = node->txbuffer.front();
				node->txbuffer.pop();
				for (const auto& value : data){ std::cout << value; };
				std::cout << std::endl;
				node->rxbuffer.push( data );
			}
		}
	}
}
