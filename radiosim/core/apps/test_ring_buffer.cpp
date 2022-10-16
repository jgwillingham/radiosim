#include <iostream>
#include <ring_buffer.h>
#include <common.h>


int main(){
	size_t buffer_size = 512;

	ring_buffer<std::complex<float>> buf(buffer_size);


	buf.put( std::complex<float>(1.0,1.0) );
	buf.put( std::complex<float>(2.0,1.0) );

	std::cout << "Getting 5 items:" <<std::endl;
	vector_c64 output1 = buf.get(5);
	for (auto& val : output1){
		std::cout << val << std::endl;
	}

	std::cout << "Getting 5 items:" << std::endl;
	vector_c64 output2 = buf.get(5);
	for (auto& val : output2){
		std::cout << val << std::endl;
	}
	

}
