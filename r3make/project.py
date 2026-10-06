import os
from r3make.target import R3BuildTarget

class R3Project:
    def __init__(self, r3make: dict, path: str) -> None:
        self.r3make: dict = r3make
        self.path: str = os.path.abspath(path)

        self.name: str = r3make.get("project")

        self.all: str = r3make.get("all", [])
        self.root: str = r3make.get("root", ".")

        self.targetData: dict[str, dict] = {}
        self.targets: dict[str, R3BuildTarget] = {}
        for name,value in self.r3make.items():
            if not isinstance(value, dict): continue

            target = R3BuildTarget(name, value)
            if target.name is None:
                target.name = name

            self.targets[name] = target
            self.targetData[name] = {
                "name": target.name,
                "type": target.type,
                "dest": target.dest,
                "artifact": target.artifact
            }

    @property
    def data(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "targets": self.targetData,
        }