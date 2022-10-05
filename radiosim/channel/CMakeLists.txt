cmake_minimum_required(VERSION 3.12)

project(Channel VERSION 0.0) # version of my project

find_package(cppzmq REQUIRED)
		
add_subdirectory(lib)
add_subdirectory(apps)
