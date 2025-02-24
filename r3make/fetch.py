import r3make.utils as utils
from r3make.compiler import SUPPORTED_COMPILERS, BaseCompiler

DEFAULT_SEARCH_PATHS: dict[str, list[str]] = {}

def fetch_compiler(compiler_name) -> bool:
    """ Tests to see if a compiler exists/is callable by outputting version info by running: `{compiler.prefix} -v`"""
    try:
        result = utils.subprocess.run(
            f"{compiler_name.lower()} -v",
            text=True,
            check=True,
            capture_output=True,
            shell=True
        )
        output = result.stderr
        return True
    except utils.subprocess.CalledProcessError:
        return False

def define_search_paths() -> None:
    """
    Defines the default search paths for all supported compilers and platforms,
    including both archives and binaries.
    """

    # common os-specific default paths
    os_paths = {
        "Windows": [
            utils.os_path("C:\\Windows\\System32"),         # this causes linker errors when used as the -L directory for some reason?
            utils.os_path("C:\\Windows\\System32\\wbem")    # so based on the above notice, windows users should put their installed/custom libs here
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
    global DEFAULT_SEARCH_PATHS
    DEFAULT_SEARCH_PATHS["OS"] = os_paths.get(utils.platform.system(), [])

    # get paths from environment variables
    env_paths = {
        "Windows": ["LIB"],  # MSVC uses LIB for library paths
        "Linux": ["LD_LIBRARY_PATH"],
        "Darwin": ["DYLD_LIBRARY_PATH"]
    }
    
    for env_var in env_paths.get(utils.platform.system(), []):
        paths = utils.os.environ.get(env_var, "").split(utils.os.pathsep)
        DEFAULT_SEARCH_PATHS["ENV"] = [utils.os_path(p) for p in paths if p]

    # get the defualt search dirs from each supported compiler
    for name, compiler in SUPPORTED_COMPILERS.items():
        if not fetch_compiler(name): continue

        DEFAULT_SEARCH_PATHS[name] = []
        search_command = f"{compiler.prefix} -print-search-dirs"

        try:
            result = utils.subprocess.run(
                search_command,
                text=True,
                check=True,
                capture_output=True,
                shell=True
            )
            output = result.stdout
        except utils.subprocess.CalledProcessError:
            # fallback to utils.os.popen if utils.subprocess fails (python and environment variables arent cool)
            try:
                with utils.os.popen(search_command) as proc:
                    output = proc.read()
                continue
            except FileNotFoundError:
                print(f"Unable to call compiler: {name}")
                continue

        for line in output.splitlines():
            if line.startswith("libraries: =") or line.startswith("programs: ="):
                paths = line.split("=", 1)[1].strip().split(utils.os.pathsep)
                DEFAULT_SEARCH_PATHS[name].extend(paths)

def fetch_library(lib:str, path: str) -> list[str]:
    """
    Recursively searches for library files (.dll, .a, .lib, .so) in the specified directory.
    Returns True if any library is found, otherwise False.
    """
    if isinstance(path, str) and utils.os.path.exists(path):
        current_dirs = [utils.os_path(path), utils.os.getcwd()]
    else:
        current_dirs = [utils.os.getcwd()]

    for search_path in DEFAULT_SEARCH_PATHS.values():
        current_dirs.extend(search_path)

    # Search recursively across all applicable directories
    for directory in set(current_dirs):
        for root, _, files in utils.os.walk(directory.strip()):
            for file in files:
                if file.endswith(('.dll', '.a', '.lib', '.so')) and file.split(".")[0] == lib:
                    if root in DEFAULT_SEARCH_PATHS["OS"]:  # OS default libs dont need a link path
                        return [lib, "OS"]
                    return [lib, root]
    return [lib, None]  # lib not found on the system

def fetch_compiler_instance(compiler_name) -> BaseCompiler:
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
