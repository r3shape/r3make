import os
import subprocess
import platform
from pathlib import Path
from r3make.util import detect_compiler, expand_files, log

def build_project(cfg, verbose=False):
    compiler = detect_compiler()
    sources = expand_files(cfg.get("sources", []), ".c")
    includes = cfg.get("includes", [])
    defines = cfg.get("defines", [])
    flags = cfg.get("flags", [])
    outdir = cfg.get("outdir", "build")
    target = cfg.get("target", "a.out")
    outtype = cfg.get("type", "exe")

    if not sources:
        log("No source files found!", "error")
        exit(1)

    os.makedirs(outdir, exist_ok=True)
    obj_files = []

    for src in sources:
        obj = os.path.join(outdir, Path(src).stem + ".o")
        cmd = [compiler, "-c", src, "-o", obj]
        for inc in includes:
            cmd += ["-I", inc]
        for d in defines:
            cmd += ["-D", d]
        cmd += flags
        if verbose:
            log(f"Compile command: {' '.join(cmd)}", "info")
        log(f"Compiling {src}")
        if subprocess.call(cmd) != 0:
            log(f"Compilation failed for {src}", "error")
            exit(1)
        obj_files.append(obj)

    ext_map = {
        "exe": ".exe" if platform.system() == "Windows" else "",
        "lib": ".a" if compiler != "cl" else ".lib",
        "dll": ".dll" if platform.system() == "Windows" else
               ".so" if platform.system() == "Linux" else
               ".dylib"}
    ext = ext_map.get(outtype, "")
    output = os.path.join(outdir, target + ext)
    link_cmd = [compiler] + obj_files + ["-o", output]

    if verbose:
        log(f"Link command: {' '.join(link_cmd)}", "info")

    log(f"Linking -> {output}")
    if subprocess.call(link_cmd) != 0:
        log("Linking failed", "error")
        exit(1)

    log("Build completed successfully!", "success")
