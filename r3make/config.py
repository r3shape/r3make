import r3make.utils as utils
from rich.panel import Panel
from rich.console import Console

CBUILD_DEFAULT_CONFIG:dict = {
    "r3make": {
        "pre-build": {},
        "post-build": {}
    },
    "c-instance": "GCC",
    "c-flags": [],
    "c-defines": [],
    "src-dirs": [],
    "src-files": [],
    "inc-dirs": [],
    "lib-links": {},
    "out-dir": "bin",
    "out-type": "exe",
    "out-name": "program",
}

def parse_config(config_path:str) -> dict | None:
    if not config_path.endswith(".r3make"):
        Console().print(Panel(f"[bold red]r3make[/] r3make configurations must have the extension `.r3make` !!!", expand=False))
        return None
    if not utils.os.path.exists(config_path): return None

    with open(config_path, "rb") as f:
        config = utils.json.load(f)
        f.close()
    
    # parse the config and set default values
    pconfig = {key: config.get(key, CBUILD_DEFAULT_CONFIG[key]) for key in CBUILD_DEFAULT_CONFIG}
    pconfig["r3make"] = {k: config["r3make"].get(k, {}) for k in CBUILD_DEFAULT_CONFIG["r3make"] if config.get("r3make", None)}
    
    # parse compiler instace configuration
    pconfig["c-flags"] = [ c_flag.strip() for c_flag in pconfig["c-flags"] ]
    pconfig["c-defines"] = [ c_define.strip() for c_define in pconfig["c-defines"] ]
    
    # parse source file configuration
    pconfig["src-dirs"] = [ utils.os_path(src_dir) for src_dir in pconfig["src-dirs"] ]
    pconfig["src-files"] = [ utils.os_path(src_file) for src_file in pconfig["src-files"] ]
    
    # parse include file configuration
    pconfig["inc-dirs"] = [ utils.os_path(src_dir) for src_dir in pconfig["inc-dirs"] ]
    
    # parse output configuration
    pconfig["out-dir"] = utils.os_path(pconfig["out-dir"])
    
    for lib, lib_path in pconfig["lib-links"].items():
        pconfig["lib-links"][lib] = utils.os_path(lib_path) if isinstance(lib_path, str) else None

    return pconfig
