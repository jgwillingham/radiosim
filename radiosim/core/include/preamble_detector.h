#include <thread>
#include <atomic>
#include <zmq.hpp>

#include "common.h"
#include "atomic_queue.h"

#ifndef _PREAMBLEDETECTOR_INCLUDED_
#define _PREAMBLEDETECTOR_INCLUDED_

class PreambleDetector{
	public:
		PreambleDetector(unsigned int iport, int corrlen);
		~PreambleDetector();

		void start();

		atomic_queue<vector_c64> inbuffer;
		atomic_queue<vector_c64> outbuffer;

	private:
		unsigned int iport;
		int corrlen;

		zmq::socket_t insocket;
		std::thread listen_thread;
		std::atomic<bool> is_active;
};


#endif
