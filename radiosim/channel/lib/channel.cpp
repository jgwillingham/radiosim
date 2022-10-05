#include <iostream>
#include <vector>
#include <zmq.hpp>
#include <channel.h>


Channel::Channel(){};

void Channel::add_node(short txport, short rxport, int buffer_size){
	NodeProxy* new_node = new NodeProxy(&ctx, txport, rxport, buffer_size);
	nodes.push_back( new_node );
	std::cout << "Added new node to channel network" << std::endl;
}


void Channel::start(){
	int num_nodes = nodes.size();
	for (int i=0; i<num_nodes; i++ ){
		std::cout << "Starting node " << i << std::endl;
		nodes[i]->start();
	}
}
