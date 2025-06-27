#!/bin/bash
set -e

BUILD_DIR=build_cpp

mkdir -p $BUILD_DIR
cd $BUILD_DIR
cmake ..
make -j$(nproc)
cd .. 