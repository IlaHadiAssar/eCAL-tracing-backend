cmake_minimum_required(VERSION 3.15)
project(MyProject)

set(CMAKE_CXX_STANDARD 20)

# Conan toolchain
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)

# Dependencies

add_executable(myapp src/main.cpp)
