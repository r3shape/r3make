import os
import json

import cbuild.utils as utils

SEP = os.path.sep

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
    pconfig["output_dir"] = utils.os_path(pconfig["output_dir"])
    pconfig["source_dirs"] = [ utils.os_path(src_dir) for src_dir in pconfig["source_dirs"] ]
    pconfig["include_dirs"] = [ utils.os_path(inc_dir) for inc_dir in pconfig["include_dirs"] ]
    pconfig["source_files"] = [ utils.os_path(src_file) for src_file in pconfig["source_files"] ]
    
    for lib, lib_path in pconfig["libraries"].items():
        pconfig["libraries"][lib] = utils.os_path(lib_path) if isinstance(lib_path, str) else None

    return pconfig
