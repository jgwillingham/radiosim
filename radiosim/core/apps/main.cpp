#include <iostream>
#include <thread>
#include <chrono>
#include <channel.h>

int main(){
	unsigned int txport = 11111;
	unsigned int rxport = 22222;
	int bufsize = 4096;

	float noise_energy = 0.1;

	Channel channel(noise_energy);
	channel.add_node(txport, rxport, bufsize);
	channel.add_node(txport+1, rxport+1, bufsize);

	channel.start();
	while (true) {
		std::this_thread::sleep_for( std::chrono::milliseconds(1000) );
};
}

