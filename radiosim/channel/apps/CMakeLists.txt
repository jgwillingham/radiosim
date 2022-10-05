# make executable from main.cpp
add_executable(main main.cpp)

target_link_libraries(main PRIVATE channel)

target_include_directories(main PUBLIC ../include)
