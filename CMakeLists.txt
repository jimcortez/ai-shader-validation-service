cmake_minimum_required(VERSION 3.16)
project(ai_shadermaker_bindings)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development.Module Development.Embed)

# Add pybind11
add_subdirectory(external/pybind11)

# Create the Python module
pybind11_add_module(ai_shadermaker_bindings 
    src/bindings/vvisf_bindings.cpp
)

# Set output directory
set_target_properties(ai_shadermaker_bindings PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/src
)

# Include directories
target_include_directories(ai_shadermaker_bindings PRIVATE
    ${CMAKE_SOURCE_DIR}/src/bindings
)

# Compiler flags
target_compile_options(ai_shadermaker_bindings PRIVATE
    -Wall
    -Wextra
    -O2
)

# Link libraries (for future VVISF-GL integration)
# target_link_libraries(ai_shadermaker_bindings PRIVATE
#     vvisf_gl
# ) 