import os
import json
import glob
import signal
import shutil
import platform
import subprocess
from pathlib import Path

COLOR = {
    "info": "\033[94m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "error": "\033[91m",
    "reset": "\033[0m"
}

def log(msg, kind="info"):
    print(f"{COLOR.get(kind, '')}[{kind.upper()}]{COLOR['reset']} {msg}")

def detect_compiler():
    for comp in ["gcc", "clang", "cl", "emcc"]:
        if shutil.which(comp):
            log(f"Compiler detected: {comp}", "success")
            return comp
    log("No supported compiler found in PATH.", "error")
    exit(1)

def load_config(target, path):
    cfg = None
    path = os_path(path)
    try:
        with open(path, 'r') as f:
            c = json.load(f)
        
        cfg = c.get(target, None)
        if cfg == None:
            cfg = c.get("main", None)
    except FileNotFoundError:
        log(f"Config file '{path}' not found.", "error")
        exit(1)
    except json.JSONDecodeError:
        log(f"Config file '{path}' is not valid JSON.", "error")
        exit(1)
    return cfg

def os_path(path) -> str:
    return path.replace("/", os.sep).replace("\\", os.sep)

def expand_files(files, ext):
    expanded = []
    for pattern in files:
        expanded += glob.glob(pattern, recursive=True)
    return [os_path(file) for file in expanded if file.endswith(ext)]
