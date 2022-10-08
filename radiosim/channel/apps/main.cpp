#include <iostream>
#include <thread>
#include <chrono>
#include <channel.h>

int main(){
	unsigned int txport = 11111;
	unsigned int rxport = 22222;
	int bufsize = 512;

	Channel channel;
	channel.add_node(txport, rxport, bufsize);
	channel.add_node(txport+1, rxport+1, bufsize);

	channel.start();
	while (true) {
		std::this_thread::sleep_for( std::chrono::milliseconds(1000) );
};
}

