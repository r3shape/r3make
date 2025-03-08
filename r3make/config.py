import r3make.utils as utils
from rich.panel import Panel
from rich.console import Console

R3MAKE_DEFAULT_CONFIG:dict = {
    "c-instance": "GCC",
    "c-targets": {}
}

R3MAKE_DEFAULT_TARGET: dict = {
    "r3make": {
        "flags": {},
        "pre-build": {},
        "post-build": {}
    },
    "c-flags": [],
    "c-defines": [],
    "src-dirs": [],
    "src-files": [],
    "inc-dirs": [],
    "lib-links": {},
    "out-dir": "bin",
    "out-type": "exe",
    "out-name": "program"
}

def parse_config(config_path:str, target: str="debug") -> dict | None:
    if not utils.os.path.exists(config_path): return None

    with open(config_path, "rb") as f:
        config = utils.json.load(f)
        f.close()
    
    # parse the config and set default values
    pconfig = {key: config.get(key, R3MAKE_DEFAULT_CONFIG[key]) for key in R3MAKE_DEFAULT_CONFIG}
    
    if target not in pconfig["c-targets"]:
        Console().print(Panel(f"[bold red]r3make[/] Invalid compilation target: {target}", expand=False))
        return
    tconfig = pconfig["c-targets"][target]
    tconfig = {key: tconfig.get(key, R3MAKE_DEFAULT_TARGET[key]) for key in R3MAKE_DEFAULT_TARGET}
    tconfig["r3make"] = {k: tconfig["r3make"].get(k, {}) for k in R3MAKE_DEFAULT_TARGET["r3make"] if tconfig.get("r3make", None)}

    # parse compiler instace configuration
    tconfig["c-instance"] = pconfig["c-instance"]
    tconfig["c-flags"] = [ c_flag.strip() for c_flag in tconfig["c-flags"] ]
    tconfig["c-defines"] = [ c_define.strip() for c_define in tconfig["c-defines"] ]
    
    # parse source file configuration
    tconfig["src-dirs"] = [ utils.os_path(src_dir) for src_dir in tconfig["src-dirs"] ]
    tconfig["src-files"] = [ utils.os_path(src_file) for src_file in tconfig["src-files"] ]
    
    # parse include file configuration
    tconfig["inc-dirs"] = [ utils.os_path(src_dir) for src_dir in tconfig["inc-dirs"] ]
    
    # parse output configuration
    tconfig["out-dir"] = utils.os_path(tconfig["out-dir"])
    
    for lib, lib_path in tconfig["lib-links"].items():
        tconfig["lib-links"][lib] = utils.os_path(lib_path) if isinstance(lib_path, str) else None

    return tconfig
