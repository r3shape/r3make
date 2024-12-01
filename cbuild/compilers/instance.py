from rich.console import Console

class CompilerInstance:
    def __init__(
            self,
            name:str,
            prefix:str,
            flags:list = [],
            outtypes:list = []
        ):
        self.name:str = name
        self.flags:list = flags
        self.prefix:str = prefix
        self.outtypes:list = outtypes

    def compile(self, console:Console, defines:list, sources:list[str], includes:list[str], outdir:str) -> list[str]:
        raise NotImplementedError
    
    def link(self, outname:str, output:str, libraries:dict[str, str], objects:list[str], outdir:str) -> str | None:
        raise NotImplementedError
