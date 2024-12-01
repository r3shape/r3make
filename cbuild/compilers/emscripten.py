from cbuild.compilers.instance import CompilerInstance

class EMCCCompiler(CompilerInstance):
    def __init__(self, flags: dict = ..., outtypes: list = ...):
        super().__init__("Emscripten", "emcc", flags, outtypes)

    def compile(self, output: str, sources: list[str], outdir: str) -> str:
        return "EMCC COMPILE"
    
    def link(self, objects: list[str], outdir: str) -> str:
        return "EMCC LINK"