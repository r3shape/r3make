import os
import platform
import subprocess
from cbuild.compilers import SUPPORTED_COMPILERS, CompilerInstance

DEFAULT_SEARCH_PATHS: dict[str, list[str]] = {}

def define_search_paths() -> None:
    """
    Defines the default search paths for all supported compilers and platforms,
    including both archives and binaries.
    """
    global DEFAULT_SEARCH_PATHS

    # common os-specific default paths
    os_default_paths = {
        "Windows": [
            "C:\\Windows\\System32",
            "C:\\Windows\\System32\\wbem"
        ],
        "Linux": [
            "/lib",
            "/usr/lib",
            "/usr/local/lib"
        ],
        "Darwin": [
            "/lib",
            "/usr/lib",
            "/usr/local/lib",
            "/opt/homebrew/lib"  # Homebrew on ARM macOS
        ]
    }

    # os-specific defaults
    DEFAULT_SEARCH_PATHS["OS_DEFAULTS"] = os_default_paths.get(platform.system(), [])

    for name, compiler in SUPPORTED_COMPILERS.items():
        DEFAULT_SEARCH_PATHS[name] = {
            "libraries": [],
            "programs": []
        }

        prefix = compiler.prefix
        search_command = f"{prefix} -print-search-dirs"

        try:
            result = subprocess.run(
                search_command,
                text=True,
                check=True,
                capture_output=True,
                shell=True
            )
            output = result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            # fallback to os.popen if subprocess fails (python and PATH arent cool)
            try:
                with os.popen(search_command) as proc:
                    output = proc.read()
            except FileNotFoundError:
                print(f"Compiler '{prefix}' not found in PATH.")
                continue

        for line in output.splitlines():
            if line.startswith("libraries: ="):
                paths = line.split("=", 1)[1].strip().split(os.pathsep)
                DEFAULT_SEARCH_PATHS[name]["libraries"].extend(paths)
            elif line.startswith("programs: ="):
                paths = line.split("=", 1)[1].strip().split(os.pathsep)
                DEFAULT_SEARCH_PATHS[name]["programs"].extend(paths)

def fetch_compiler_instance(compiler_name) -> CompilerInstance:
    try:
        return SUPPORTED_COMPILERS[compiler_name]
    except (KeyError) as e:
        print(f"Unsupported compiler: {compiler_name}")
        return None

def fetch_files(extension:str, directory:str) -> list[str]:
    source_files = []
    if not os.path.exists(directory): return source_files
    for root, _, files in os.walk(directory.strip()):
        for file in files:
            if file.endswith(extension):
                source_files.append(os.path.join(root, file))
    return source_files

def fetch_library(lib:str, path: str) -> bool:
    """
    Recursively searches for library files (.dll, .a, .lib) in the specified directory.
    Returns True if any library is found, otherwise False.
    """
    if not os.path.exists(path.strip()):
        return False

    define_search_paths()
    current_dirs = [os.getcwd(), path]

    for search_path in DEFAULT_SEARCH_PATHS.values():
        current_dirs.extend(search_path)

    # Search recursively across all applicable directories
    for directory in set(current_dirs):
        for root, _, files in os.walk(directory.strip()):
            for file in files:
                if file.endswith(('.dll', '.a', '.lib')) and file.split(".")[0] == lib:
                    return True
