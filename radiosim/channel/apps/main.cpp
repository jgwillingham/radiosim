#include <iostream>
#include <thread>
#include <chrono>
#include <channel.h>

int main(){
	short txport(12345);
	short rxport(54321);
	int bufsize(512);

	Channel channel;
	channel.add_node(txport, rxport, bufsize);
	channel.add_node(22222, 33333, 512);
	channel.start();
	while (true) {
		std::this_thread::sleep_for( std::chrono::milliseconds(1000) );
};
}

