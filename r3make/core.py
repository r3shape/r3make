import os, sys
import subprocess
import platform
from pathlib import Path
from r3make.version import YEAR, MINOR, PATCH
from r3make.util import detect_compiler, os_path, expand_files, log

def build_project(cfg, target, run=False, verbose=False, clean_obj=False, build_each=False):
    if verbose: log(f"r3make {YEAR}.{MINOR}.{PATCH} | python {sys.version}")
    print(run)
    compiler = detect_compiler()
    flags = cfg.get("flags", [])
    defines = cfg.get("defines", [])
    includes = cfg.get("includes", [])
    sources = expand_files(cfg.get("sources", []), ".c")
    type = cfg.get("type", "exe")
    dest = os_path(cfg.get("dest", "build"))
    libraries = cfg.get("libraries", {})
    
    if not sources:
        log("No source files found!", "error")
        exit(1)
    
    os.makedirs(dest, exist_ok=True)

    ext_map = {
        "exe": ".exe" if platform.system() == "Windows" else "",
        "lib": ".a" if compiler != "cl" else ".lib",
        "dll": ".dll" if platform.system() == "Windows" else
               ".so" if platform.system() == "Linux" else
               ".dylib"
    }
    ext = ext_map.get(type, "")

    link_flags = []
    for lib, path in libraries.items():
        if path is not None and not os.path.exists(path):
            log(f"Library ({lib}) cannot be located at {path}", "error")
            exit(1)
        link_flags.append(f"-l{lib}")
        if path:
            link_flags.append(f"-L{os_path(path)}")

    if build_each:
        for src in sources:
            base = Path(src).stem
            obj = os.path.join(dest, base + ".o")
            output = os.path.join(dest, base + ext)

            compile_cmd = [compiler, "-c", src, "-o", obj]
            for inc in includes:
                compile_cmd += ["-I", inc]
            for d in defines:
                compile_cmd += ["-D", d]
            compile_cmd += flags

            if verbose:
                log(f"Compile command: {' '.join(compile_cmd)}", "info")
            log(f"Compiling {src}")
            if subprocess.call(' '.join(compile_cmd)) != 0:
                log(f"Compilation failed for {src}", "error")
                exit(1)

            link_cmd = f"{compiler} {obj} {' '.join(link_flags)} -o {output}" if type == "exe" else \
                       f"{compiler} -shared {obj} {' '.join(link_flags)} -o {output}" if type == "dll" else \
                       f"ar rcs {output} {obj}"

            if verbose:
                log(f"Link command: {link_cmd}", "info")
            log(f"Linking -> {output}")
            if subprocess.call(link_cmd) != 0:
                log(f"Linking failed for {base}", "error")
                exit(1)

            log(f"Built {output}", "success")

            if run == True and type == "exe":
                log(f"Running {output}...\n", "info")
                subprocess.call([output])
            elif run == True and type != "exe":
                log(f"--run is only supported for 'exe' targets.", "warning")

            if clean_obj:
                try:
                    os.remove(obj)
                    log(f"Removed {obj}", "info")
                except Exception as e:
                    log(f"Failed to remove {obj}: {e}", "warning")
    else:
        obj_files = []
        for src in sources:
            obj = os.path.join(dest, Path(src).stem + ".o")
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

        name = cfg.get("name", target)
        output = os.path.join(dest, name + ext)
        link_cmd = f"{compiler} {' '.join(obj_files)} {' '.join(link_flags)} -o {output}" if type == "exe" else \
                   f"{compiler} -shared {' '.join(obj_files)} {' '.join(link_flags)} -o {output}" if type == "dll" else \
                   f"ar rcs {output} {' '.join(obj_files)}"

        if verbose:
            log(f"Link command: {link_cmd}", "info")
        log(f"Linking -> {output}")
        if subprocess.call(link_cmd) != 0:
            log("Linking failed", "error")
            exit(1)
        log("Build completed", "success")

        if run == True and type == "exe":
            log(f"Running {output}...\n", "info")
            subprocess.call([output])
        elif run == True and type != "exe":
            log(f"--run is only supported for 'exe' targets.", "warning")

        if clean_obj:
            for obj in obj_files:
                try:
                    os.remove(obj)
                    log(f"Removed {obj}", "info")
                except Exception as e:
                    log(f"Failed to remove {obj}: {e}", "warning")
