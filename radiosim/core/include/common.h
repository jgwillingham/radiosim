
#ifndef COMMON_INCLUDED
#define COMMON_INCLUDED

#include <vector>
#include <complex>
#include <algorithm>


typedef std::vector<std::complex<float>> vector_c64;


// overload + operator to sum complex vectors elementwise
inline vector_c64 operator+(const vector_c64& vec1, const vector_c64& vec2){
	assert(vec1.size() == vec2.size());
	size_t dim = vec1.size();
	vector_c64 vsum(dim);
	std::transform(vec1.begin(), vec1.end(), vec2.begin(), vsum.begin(), std::plus<std::complex<float>>());
	return vsum;
}

#endif
