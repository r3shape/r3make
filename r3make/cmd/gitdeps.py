import os, shutil
import subprocess
from r3make.util import log, load_config

def get_os_lib_dir():
    if os.name == "nt":
        return os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "wbem")
    elif os.name == "posix":
        return "/usr/local/lib/r3make"
    return os.path.abspath("gitdeps")

def get_lib_dir():
    os_dir = get_os_lib_dir()
    test_file = os.path.join(os_dir, ".r3make_test")

    try:
        os.makedirs(os_dir, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return os_dir
    except PermissionError:
        fallback = os.path.abspath("gitdeps")
        os.makedirs(fallback, exist_ok=True)
        log(f"Falling back to local gitdeps directory (elevated shell required for OS-default path): {fallback}", "warning")
        return fallback

def gitdeps(main_target, main_config, verbose=False):
    gitdeps = main_config.get("gitdeps", None)
    if not gitdeps: return
    
    base_dir = get_lib_dir()
    for repo in gitdeps:
        user, name = repo.split("/")
        repo_url = f"https://github.com/{user}/{name}.git"
        clone_path = os.path.join(base_dir, name)

        if not os.path.exists(clone_path):
            log(f"Cloning {repo} into {clone_path}...", "info")
            result = subprocess.run(["git", "clone", repo_url, clone_path])
            if result.returncode != 0:
                log(f"Failed to clone {repo_url}", "error")
                exit(1)
        else:
            log(f"Updating {repo} in {clone_path}...", "info")
            result = subprocess.run(["git", "-C", clone_path, "pull"])
            if result.returncode != 0:
                log(f"Failed to update {repo}", "warning")

        config_path = os.path.join(clone_path, "r3make.json")
        if not os.path.exists(config_path):
            log(f"No r3make.json found in {clone_path}, skipping build.", "warning")
            continue

        dep_config = load_config(name, config_path)
        if not dep_config:
            log(f"Target '{name}' not found in {config_path}", "warning")
            continue

        from r3make.core import build_project

        olddir = os.getcwd()
        os.chdir(clone_path)
        build_project(dep_config, name, verbose=verbose, nofiles=1)

        # === Patch main_config with library info ===
        lib_name = dep_config.get("name", name)
        lib_dest = dep_config.get("dest", "build")
        lib_path = os.path.join(clone_path, lib_dest)
        
        src_artifact = os.path.realpath(os.path.join(lib_dest, f"{name}.{str(dep_config.get("type")).lower()}"))
        os.chdir(olddir)

        if str(dep_config.get("type", None)).lower() in ("dll", "lib"):
            if not os.path.exists(main_config.get("dest")):
                os.mkdir(main_config.get("dest"))
            shutil.copy2(
                src=src_artifact,
                dst=main_config.get("dest")
            )

        if "libraries" not in main_config:
            main_config["libraries"] = {}

        if "includes" not in main_config:
            main_config["includes"] = []

        main_config["libraries"][lib_name] = lib_path
        main_config["includes"].insert(0, clone_path)
        log(f"Added library '{lib_name}' from {repo} -> {lib_path}", "info")
