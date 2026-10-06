import os
from r3make.project import R3Project
from r3make.target import R3BuildTarget

class R3Reference:
    def __init__(self, project: R3Project, target: R3BuildTarget):
        self.project: R3Project = project
        self.target: R3BuildTarget = target
        self.path: str = os.path.join(
            self.project.path,
            self.project.root
        )

    def getArtifactPath(self) -> str:
        return os.path.join(
            self.path,
            self.target.dest,
            self.target.name + self.target.artifact,
        )
    
    def getArtifactDir(self) -> str:
        return os.path.join(
            self.path,
            self.target.dest
        )

