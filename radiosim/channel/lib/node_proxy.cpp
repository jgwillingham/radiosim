#include <zmq.hpp>
#include <node_proxy.h>


NodeProxy::NodeProxy(){};


void NodeProxy::start(){
	std::cout << "NodeProxy listening on localhost:55555" << std::endl;
	zmq::context_t ctx;

	zmq::socket_t sock(ctx, zmq::socket_type::pull);
	sock.bind("tcp://127.0.0.1:55555");

	while (true) {
		zmq::message_t msg;
		sock.recv( msg, zmq::recv_flags::none );
		std::cout << "Received data " << std::endl;
	}
}
