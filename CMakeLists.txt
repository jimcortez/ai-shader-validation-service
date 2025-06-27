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

# Temporarily disable VVISF-GL build to get basic C++ bindings working
# TODO: Re-enable VVISF-GL integration once build issues are resolved
# add_custom_target(vvgl_build
#     COMMAND env CPPFLAGS="-Wall -g -std=c++11 -fPIC -I./include/ -DVVGL_SDK_GLFW" make -C ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVGL
#     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVGL
#     COMMENT "Building VVGL library"
# )

# add_custom_target(vvisf_build
#     COMMAND env CPPFLAGS="-Wall -g -std=c++11 -fPIC -I./include/ -DVVGL_SDK_GLFW" make -C ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVISF
#     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVISF
#     COMMENT "Building VVISF library"
#     DEPENDS vvgl_build
# )

# Link libraries (for VVISF-GL integration)
# TODO: Re-enable VVISF-GL linking once build issues are resolved
# target_link_libraries(ai_shadermaker_bindings PRIVATE
#     ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVGL/libVVGL.a
#     ${CMAKE_SOURCE_DIR}/external/VVISF-GL/VVISF/libVVISF.a
# )

# Ensure VVISF-GL is built before our bindings
# add_dependencies(ai_shadermaker_bindings vvgl_build vvisf_build) 