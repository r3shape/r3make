import os
import json

CBUILD_DEFAULT_CONFIG:dict = {
    'compiler': 'MinGW',
    'project': 'MyProject',
    'output': 'exe',
    'output_dir': 'cbuild/',
    'source_dirs': [],
    'source_files': [],
    'flags': [],
    'defines': [],
    'libraries': {},
    'include_dirs': [],
}; CBUILD_CONFIG_REQUIRED_FIELDS:set = {"compiler", "project", "output"}

def parse_config(config_path:str) -> dict | None:
    if not os.path.exists(config_path): return None

    with open(config_path, "rb") as f:
        config:dict = json.load(f)
        f.close()

    pconfig = {key: config.get(key, CBUILD_DEFAULT_CONFIG[key]) for key in CBUILD_DEFAULT_CONFIG}
    
    pconfig["flags"] = [ c_flag.strip() for c_flag in pconfig["flags"] ]
    pconfig["defines"] = [ define.strip() for define in pconfig["defines"] ]
    pconfig["output_dir"] = pconfig["output_dir"].strip().replace("/", "\\")
    pconfig["source_dirs"] = [ src_dir.strip().replace("/", "\\") for src_dir in pconfig["source_dirs"] ]
    pconfig["include_dirs"] = [ inc_dir.strip().replace("/", "\\") for inc_dir in pconfig["include_dirs"] ]
    pconfig["source_files"] = [ src_file.strip().replace("/", "\\") for src_file in pconfig["source_files"] ]
    
    for lib, path in pconfig["libraries"].items():
        pconfig["libraries"][lib] = path.strip().replace("/", "\\") if isinstance(path, str) else None

    return pconfig
