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
		std::string msg_bytes = msg.to_string();
		vector_c64 data = unpack_to_complex64(msg_bytes);
		txbuffer.push( data );
	}
}


// Unpack message bytes to vector of complex64 data
vector_c64 NodeProxy::unpack_to_complex64(std::string& msg_bytes){
	size_t nbytes = msg_bytes.length();
	size_t floatsize = sizeof(float);

	int nfloats = nbytes/floatsize;
	std::vector<float> floatdata( nfloats );
	for (int i=0; i<nfloats; i+=1){
		memcpy(&(floatdata[i]), &msg_bytes[floatsize*i], floatsize);
	}

	int ncomplex = nfloats/2;
	vector_c64 complexdata(ncomplex);
	for (int j=0; j<ncomplex; j++){
		complexdata[j] = std::complex<float>(floatdata[2*j], floatdata[2*j+1]);
	}
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
			zmq::message_t msg = pack_bytes_into_message(data);
			rxsocket.send( msg, zmq::send_flags::none );
		}
	}
}



// Serialize complex64 data into bytes (string) object
zmq::message_t NodeProxy::pack_bytes_into_message(vector_c64 complexdata){
	size_t ncomplex = complexdata.size();
	size_t nfloats = 2*ncomplex;

	std::vector<float> floatdata(nfloats);
	for (int i=0; i<ncomplex; i++){
		std::complex<float> cdatum = complexdata[i];
		floatdata[2*i] = cdatum.real();
		floatdata[2*i+1] = cdatum.imag();
	}

	zmq::message_t msg(nfloats*sizeof(float));
	memcpy(msg.data(), floatdata.data(), nfloats*sizeof(float));
	return msg;
}
