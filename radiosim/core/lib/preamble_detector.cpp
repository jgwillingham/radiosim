#include <preamble_detector.h>



PreambleDetector::PreambleDetector(unsigned int iport, int corrlen){
	init_socket(iport);
}


PreambleDetector::~PreambleDetector(){
	insocket.close();
}


void PreambleDetector::start(){
	

}
