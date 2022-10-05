#include <iostream>
#include <zmq.hpp>
#include <channel.h>


Channel::Channel(){};

void Channel::add_node(){
	NodeProxy* node = new NodeProxy();
	node->start();
}
