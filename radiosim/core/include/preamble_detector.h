
#ifndef PREAMBLEDETECTOR_INCLUDED
#define PREAMBLEDETECTOR_INCLUDED

#include <thread>
#include <atomic>
#include <zmq.hpp>
#include "common.h"
#include "threadsafe_queue.h"


class PreambleDetector{
	public:
		PreambleDetector(unsigned int iport, int corrlen);
		~PreambleDetector();

		void start
		void set_pramble();
		void schmidl_cox_correlate(vector_c64& correlations, );

		threadsafe_queue<vector_c64> inbuffer;
		threadsafe_queue<vector_c64> outbuffer;

	private:
		unsigned int iport;
		int corrlen;

		zmq::socket_t insocket;
		std::thread listen_thread;
		std::atomic<bool> is_active;
};


#endif
