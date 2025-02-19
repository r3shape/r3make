from .basecompiler import BaseCompiler

SUPPORTED_COMPILERS:dict[str, dict] = {
    "EMCC": BaseCompiler("EMCC", "emcc", ["wasm", "js", "html"]),
    "GCC": BaseCompiler("GCC", "gcc", ["exe", "dll", "dylib", "so"]),
    "CLANG": BaseCompiler("Clang", "clang", ["exe", "dll", "dylib", "so"])
}