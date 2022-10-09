cmake_minimum_required(VERSION 3.12)

project(Channel VERSION 0.0)

set(CMAKE_CXX_STANDARD 11)

find_package(cppzmq REQUIRED)

if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()
set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")
		
add_subdirectory(lib)
add_subdirectory(apps)
