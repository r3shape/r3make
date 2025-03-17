from .basecompiler import BaseCompiler

SUPPORTED_COMPILERS:dict[str, dict] = {
    "EMCC": BaseCompiler("EMCC", "emcc", ["wasm", "js", "html", "a", "lib"]),
    "GCC": BaseCompiler("GCC", "gcc", ["exe", "dll", "dylib", "so", "a", "lib"]),
    "CLANG": BaseCompiler("Clang", "clang", ["exe", "dll", "dylib", "so", "a", "lib"])
}