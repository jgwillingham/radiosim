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


// Destructor
NodeProxy::~NodeProxy(){
	tx_is_active.store(false);
	if (txlisten_thread.joinable()){ 
		txlisten_thread.join();
	}
	rx_is_active.store(false);
	if (rxsend_thread.joinable()){
		rxsend_thread.join();
	}
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
	tx_is_active.store(true);
	this->txlisten_thread = std::thread( &NodeProxy::txlisten, this);

	rx_is_active.store(true);
	this->rxsend_thread = std::thread( &NodeProxy::rxsend, this);
}


// Listen on txsocket for data
void NodeProxy::txlisten(){
	while ( tx_is_active.load() ) {
		zmq::message_t msg;
		txsocket.recv( msg, zmq::recv_flags::none );
		vector_c64 data = unpack_to_complex64(msg);
		txbuffer.push( data );
	}
}


// Unpack message bytes to vector of complex64 data
vector_c64 NodeProxy::unpack_to_complex64(zmq::message_t& msg){
	size_t nbytes = msg.size();
	vector_c64 complexdata( nbytes/2/sizeof(float) );
	memcpy(complexdata.data(), msg.data(), nbytes);
	return complexdata;
}


// Send channel data out rxsocket
void NodeProxy::rxsend(){
	vector_c64 data;
	data.reserve(512);
	while ( rx_is_active.load() ){
		// Get data in buffer. Wait/block if empty
		rxbuffer.wait_pop( data );
		// Pack data bytes into msg and send
		zmq::message_t msg = pack_complex64_to_message(data);
		rxsocket.send( msg, zmq::send_flags::none );
	}
}



// Write ZMQ message object from vector of complex64 data
zmq::message_t NodeProxy::pack_complex64_to_message(vector_c64& complexdata){
	size_t nbytes = 2*complexdata.size()*sizeof(float);
	zmq::message_t msg(nbytes);
	memcpy(msg.data(), complexdata.data(), nbytes);
	return msg;
}
