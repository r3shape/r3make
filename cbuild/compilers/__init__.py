from .mingw import GCCCompiler
from .emscripten import EMCCCompiler
from .instance import CompilerInstance

SUPPORTED_COMPILERS:dict[str, dict] = {
    "MinGW": GCCCompiler(outtypes=["exe", "dll"]),
    "Emscripten": EMCCCompiler(outtypes=["js", "wasm", "html"])
}


