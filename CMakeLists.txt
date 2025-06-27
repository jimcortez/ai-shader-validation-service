cmake_minimum_required(VERSION 3.16)
project(ai-shadermaker-bindings)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python 3.11 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# Find VVISF-GL
find_package(VVISF REQUIRED)
find_package(VVGL REQUIRED)

# Include directories
include_directories(${VVISF_INCLUDE_DIRS})
include_directories(${VVGL_INCLUDE_DIRS})

# Create the Python module
pybind11_add_module(vvisf_engine 
    src/bindings/vvisf_bindings.cpp
    src/bindings/validation_result.cpp
    src/bindings/image_data.cpp
)

# Link libraries
target_link_libraries(vvisf_engine 
    ${VVISF_LIBRARIES}
    ${VVGL_LIBRARIES}
    ${OpenGL_LIBRARIES}
    ${CMAKE_DL_LIBS}
)

# Set compiler flags
target_compile_options(vvisf_engine PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra>
    $<$<CXX_COMPILER_ID:Clang>:-Wall -Wextra>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# Install the module
install(TARGETS vvisf_engine
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages
) 