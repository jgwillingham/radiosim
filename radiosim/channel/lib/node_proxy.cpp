#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <complex>
#include <chrono>
#include <zmq.hpp>
#include <node_proxy.h>


// Constructor
NodeProxy::NodeProxy(zmq::context_t& ctx, unsigned int txport, unsigned int rxport, int buffer_size){
	init_sockets(ctx, txport, rxport);
	init_buffers(buffer_size);
}


// Initialize sockets
void NodeProxy::init_sockets(zmq::context_t& ctx, unsigned int txport, unsigned int rxport){
	this->txport = txport;
	this->rxport = rxport;

	txsocket = zmq::socket_t(ctx, zmq::socket_type::pull);
	txsocket.bind( "tcp://127.0.0.1:" + std::to_string(txport) );

	rxsocket = zmq::socket_t(ctx, zmq::socket_type::push);
	rxsocket.bind( "tcp://127.0.0.1:" + std::to_string(rxport) );
}


// Initialize buffers
void NodeProxy::init_buffers(int buffer_size){
	//txbuffer.reserve(buffer_size);
	//rxbuffer.reserve(buffer_size);
}


// Startup node proxy threads
void NodeProxy::start(){
	std::thread txlisten_thread( &NodeProxy::txlisten, this);
	std::thread rxsend_thread( &NodeProxy::rxsend, this);
	txlisten_thread.detach();
	rxsend_thread.detach();
}


// Listen on txsocket for data
void NodeProxy::txlisten(){
	std::cout << "NodeProxy listening on localhost:" << txport << std::endl;

	while (true) {
		zmq::message_t msg;
		txsocket.recv( msg, zmq::recv_flags::none );
		vector_c64 data = unpack_to_complex64(msg);
		txbuffer.push( data );
	}
}


// Unpack message bytes to vector of complex64 data
inline vector_c64 NodeProxy::unpack_to_complex64(zmq::message_t& msg){
	size_t nbytes = msg.size();
	vector_c64 complexdata( nbytes/2/sizeof(float) );
	memcpy(complexdata.data(), msg.data(), nbytes);
	return complexdata;
}


// Send channel data out rxsocket
void NodeProxy::rxsend(){
	std::cout << "NodeProxy sending from localhost:" << rxport << std::endl;
	vector_c64 data;
	data.reserve(512);
	while (true){
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
		if (not rxbuffer.empty()){
			data = rxbuffer.front();
			rxbuffer.pop();
			zmq::message_t msg = pack_complex64_to_message(data);
			rxsocket.send( msg, zmq::send_flags::none );
		}
	}
}



// Write ZMQ message object from vector of complex64 data
inline zmq::message_t NodeProxy::pack_complex64_to_message(vector_c64& complexdata){
	size_t nbytes = 2*complexdata.size()*sizeof(float);
	zmq::message_t msg(nbytes);
	memcpy(msg.data(), complexdata.data(), nbytes);
	return msg;
}
