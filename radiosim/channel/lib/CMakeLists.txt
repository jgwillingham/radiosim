
add_library(nodeproxy node_proxy.cpp)
target_include_directories(nodeproxy PUBLIC ../include)

add_library(channel channel.cpp)
target_include_directories(channel PUBLIC ../include)

target_link_libraries(channel PRIVATE nodeproxy cppzmq)

