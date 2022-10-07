#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <complex>
#include <zmq.hpp>
#include <node_proxy.h>


// Constructor
NodeProxy::NodeProxy(zmq::context_t &ctx, short txport, short rxport, int buffer_size){
	init_sockets(ctx, txport, rxport);
	init_buffers(buffer_size);
}


// Initialize sockets
void NodeProxy::init_sockets(zmq::context_t &ctx, short txport, short rxport){
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
	txlisten_thread.detach();
}


// Listen on txsocket for data
void NodeProxy::txlisten(){
	std::cout << "NodeProxy listening on localhost:" << txport << std::endl;

	while (true) {
		zmq::message_t msg;
		txsocket.recv( msg, zmq::recv_flags::none );
		std::string msg_str = msg.to_string();
		vector_c64 data = unpack_to_complex64(msg_str);
		txbuffer.push( data );
	}
}


// Unpack message bytes to vector of complex64 data
vector_c64 NodeProxy::unpack_to_complex64(std::string msg_str){
	size_t nbytes = msg_str.length();
	size_t floatsize = sizeof(float);

	int nfloats = nbytes/floatsize;
	std::vector<float> floatdata( nfloats );
	for (int i=0; i<nfloats; i+=1){
		memcpy(&(floatdata[i]), &msg_str[floatsize*i], floatsize);
	}

	int ncomplex = nfloats/2;
	vector_c64 complexdata(ncomplex);
	for (int j=0; j<ncomplex; j++){
		complexdata[j] = std::complex<float>(floatdata[2*j], floatdata[2*j+1]);
	}
	return complexdata;
}
