import os
import subprocess
import platform
from pathlib import Path
from r3make.util import detect_compiler, os_path, expand_files, log

def build_project(cfg, verbose=False):
    compiler = detect_compiler()
    sources = expand_files(cfg.get("sources", []), ".c")
    includes = cfg.get("includes", [])
    defines = cfg.get("defines", [])
    flags = cfg.get("flags", [])
    outdir = os_path(cfg.get("outdir", "build"))
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
        if subprocess.call(' '.join(cmd)) != 0:
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
    
    libraries = cfg.get("libraries", {})
    link_flags = []

    for lib, path in libraries.items():
        if path is not None and not os.path.exists(path):
            log(f"Library ({lib}) cannot be located at {path}")
            exit(1)
        link_flags.append(f"-l{lib}")
        link_flags.append(f"-L{os_path(path)}") if path is not None else ...

    obj_str = ' '.join(obj_files)
    lib_str = ' '.join(link_flags)

    cmd_map = {
        "exe": f"{compiler} {obj_str} {lib_str} -o {output}",
        "lib": f"ar rcs {output} {obj_str}",
        "dll": f"{compiler} -shared {obj_str} {lib_str} -o {output}" if platform.system() == "Windows"
               else f"{compiler} -shared {obj_str} {lib_str} -o {output}" if platform.system() == "Linux"
               else f"{compiler} -dynamiclib {obj_str} {lib_str} -o {output}"  # macOS
    }
    
    link_cmd = cmd_map[outtype]

    if verbose:
        log(f"Link command: {link_cmd}", "info")
    log(f"Linking -> {output}")
    if subprocess.call(link_cmd) != 0:
        log("Linking failed", "error")
        exit(1)
    log("Build completed successfully!", "success")
