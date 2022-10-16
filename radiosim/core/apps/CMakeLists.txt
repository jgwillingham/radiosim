# make executable from main.cpp
add_executable(main main.cpp)
add_executable(test_rb test_ring_buffer.cpp)

target_link_libraries(main PRIVATE channel)

target_include_directories(main PUBLIC ../include)
target_include_directories(test_rb PUBLIC ../include)
