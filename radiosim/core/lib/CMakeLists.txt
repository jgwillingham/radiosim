
add_library(nodeproxy node_proxy.cpp)
target_include_directories(nodeproxy PUBLIC ../include)
set_property(TARGET nodeproxy PROPERTY POSITION_INDEPENDENT_CODE ON)

add_library(channel SHARED channel.cpp)
set_property(TARGET channel PROPERTY POSITION_INDEPENDENT_CODE ON)
target_include_directories(channel PUBLIC ../include)

add_library(preamble_detector SHARED preamble_detector.cpp)
set_property(TARGET preamble_detector PROPERTY POSITION_INDEPENDENT_CODE ON)
target_include_directories(preamble_detector PUBLIC ../include)


target_link_libraries(channel PRIVATE nodeproxy cppzmq)
target_link_libraries(preamble_detector PRIVATE cppzmq)
