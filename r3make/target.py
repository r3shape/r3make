import os
import platform

class R3BuildTarget:
    def __init__(self, target: str, data: dict) -> None:
        self.target: str = target
        self.objs: list[str] = []

        self.type: str = data.get("type")
        self.dest: str = data.get("dest")
        self.sources: list[str] = data.get("sources")

        self.artifact: str = ""
        if self.type in ["so","dll","shared","dynamic"]:
            self.artifact = ".dll" if platform.system() == "Windows" else ".so"
        if self.type in ["lib","static"]:
            self.artifact = ".lib" if platform.system() == "Windows" else ".a"
        if self.type in ["exe","executable"]:
            self.artifact = ".exe" if platform.system() == "Windows" else ""

        self.name: str = data.get("name", None)
        self.deps: list[str] = data.get("deps", [])
        self.ccflags: list[str] = data.get("ccflags", [])
        self.ldflags: list[str] = data.get("ldflags", [])
        self.defines: list[str] = data.get("defines", [])
        self.includes: list[str] = data.get("includes", [])
        self.requires: list[str] = data.get("requires", [])

    def getArtifactPath(self) -> str:
        return os.path.join(self.dest, self.name + self.artifact)

    def getCCFlags(self) -> list[str]:
        return [f"-{flag}" if not flag.startswith('-') else flag for flag in self.ccflags]

    def getLDFlags(self) -> list[str]:
        return [f"-{flag}" if not flag.startswith('-') else flag for flag in self.ldflags]

    def getIncludes(self) -> list[str]:
        return [f"-I{path}" for path in self.includes]

    def getDefines(self) -> list[str]: 
        return [f"-D{define}" for define in self.defines]
