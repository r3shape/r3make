import os
import platform
import subprocess

SEP = os.path.sep
def os_path(path:str=None) -> str:
    if path is None: return None
    return path.strip().replace("/", os.path.sep).replace("\\", os.path.sep)

def os_mkdir(path:str=None) -> None:
    if path is None: return None
    if not os.path.exists(path):
        root = path.split(SEP)[0]
        dirs = path.split(SEP)[1:]
        if not os.path.exists(root): os.mkdir(root)
        for d in dirs:
            root += f"{SEP}{d}"
            if not os.path.exists(root): os.mkdir(root)
