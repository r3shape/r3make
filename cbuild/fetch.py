import cbuild.utils as utils
from cbuild.compiler import SUPPORTED_COMPILERS, BaseCompiler

DEFAULT_SEARCH_PATHS: dict[str, list[str]] = {}

def define_search_paths() -> None:
    """
    Defines the default search paths for all supported compilers and platforms,
    including both archives and binaries.
    """
    global DEFAULT_SEARCH_PATHS

    # common os-specific default paths
    utils.os_default_paths = {
        "Windows": [
            utils.os_path("C:\\Windows\\System32"),
            utils.os_path("C:\\Windows\\System32\\wbem")
        ],
        "Linux": [
            utils.os_path("/lib"),
            utils.os_path("/usr/lib"),
            utils.os_path("/usr/local/lib")
        ],
        "Darwin": [
            utils.os_path("/lib"),
            utils.os_path("/usr/lib"),
            utils.os_path("/usr/local/lib"),
            utils.os_path("/opt/homebrew/lib")  # Homebrew on ARM macutils.OS
        ]
    }

    # os-specific defaults
    DEFAULT_SEARCH_PATHS["utils.OS_DEFAULTS"] = utils.os_default_paths.get(utils.platform.system(), [])

    for name, compiler in SUPPORTED_COMPILERS.items():
        DEFAULT_SEARCH_PATHS[name] = {
            "libraries": [],
            "programs": []
        }

        prefix = compiler.prefix
        search_command = f"{prefix} -print-search-dirs"

        try:
            result = utils.subprocess.run(
                search_command,
                text=True,
                check=True,
                capture_output=True,
                shell=True
            )
            output = result.stdout
        except (utils.subprocess.CalledProcessError, FileNotFoundError):
            # fallback to utils.os.popen if utils.subprocess fails (python and environment variables arent cool)
            try:
                with utils.os.popen(search_command) as proc:
                    output = proc.read()
            except FileNotFoundError:
                print(f"Compiler '{prefix}' not found in PATH.")
                continue

        for line in output.splitlines():
            if line.startswith("libraries: ="):
                paths = line.split("=", 1)[1].strip().split(utils.os.pathsep)
                DEFAULT_SEARCH_PATHS[name]["libraries"].extend(paths)
            elif line.startswith("programs: ="):
                paths = line.split("=", 1)[1].strip().split(utils.os.pathsep)
                DEFAULT_SEARCH_PATHS[name]["programs"].extend(paths)

def fetch_compiler_instance(compiler_name) -> BaseCompiler:
    # TODO: extend to fetch OS default compiler
    try:
        return SUPPORTED_COMPILERS[compiler_name]
    except (KeyError) as e:
        print(f"Unsupported compiler: {compiler_name}")
        return None

def fetch_files(extension:str, directory:str) -> list[str]:
    directory = utils.os_path(directory)
    source_files = []
    if not utils.os.path.exists(directory): return source_files
    for root, _, files in utils.os.walk(directory.strip()):
        for file in files:
            if file.endswith(extension):
                source_files.append(utils.os.path.join(root, file))
    return source_files

def fetch_library(lib:str, path: str) -> bool:
    """
    Recursively searches for library files (.dll, .a, .lib, .so) in the specified directory.
    Returns True if any library is found, otherwise False.
    """
    path = utils.os_path(path)
    if not utils.os.path.exists(path):
        return False

    define_search_paths()
    current_dirs = [utils.os.getcwd(), path]

    for search_path in DEFAULT_SEARCH_PATHS.values():
        current_dirs.extend(search_path)

    # Search recursively across all applicable directories
    for directory in set(current_dirs):
        for root, _, files in utils.os.walk(directory.strip()):
            for file in files:
                if file.endswith(('.dll', '.a', '.lib', '.so')) and file.split(".")[0] == lib:
                    return True
