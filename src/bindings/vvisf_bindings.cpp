#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(ai_shadermaker_bindings, m) {
    m.doc() = "AI ShaderMaker C++ bindings (scaffold)";
}
