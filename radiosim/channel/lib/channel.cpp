#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <zmq.hpp>
#include <channel.h>


Channel::Channel(){};


Channel::~Channel(){
	ctx.shutdown();
	ctx.close();
};


void Channel::add_node(short txport, short rxport, int buffer_size){
	NodeProxy* new_node = new NodeProxy(ctx, txport, rxport, buffer_size);
	nodes.push_back( new_node );
	std::cout << "Added new node to channel network" << std::endl;
}


void Channel::start(){
	int num_nodes = nodes.size();
	for (int i=0; i<num_nodes; i++ ){
		std::cout << "Starting node " << i << std::endl;
		nodes[i]->start();
	}
	run_main_loop();
}


void Channel::run_main_loop(){
	while (true){
		for (auto& node : nodes){
			std::this_thread::sleep_for( std::chrono::milliseconds(100) );
			if (!node->txbuffer.empty()){
				std::cout << "\nFound data in buffer:" << std::endl;
				std::vector<std::complex<float>> data = node->txbuffer.back();
				for (auto& value : data){std::cout << value;};
				node->txbuffer.pop_back();
			}
		}
	}
}
