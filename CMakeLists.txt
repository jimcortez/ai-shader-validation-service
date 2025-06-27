cmake_minimum_required(VERSION 3.15)
project(ai_shadermaker_bindings LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# pybind11 (use as subdirectory)
add_subdirectory(external/pybind11)

# VVISF-GL (integration will be added in a later step)
# add_subdirectory(external/VVISF-GL)
# include_directories(external/VVISF-GL/include)
# find_package(VVISF REQUIRED)

# Source files
file(GLOB BINDING_SOURCES src/bindings/*.cpp)

# Create the Python module
pybind11_add_module(ai_shadermaker_bindings ${BINDING_SOURCES})

# Link libraries
# target_link_libraries(ai_shadermaker_bindings PRIVATE vvisf-gl)

# Set compiler flags
target_compile_options(ai_shadermaker_bindings PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra>
    $<$<CXX_COMPILER_ID:Clang>:-Wall -Wextra>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# Install the module
install(TARGETS ai_shadermaker_bindings DESTINATION .) 