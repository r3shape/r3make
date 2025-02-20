import r3make.utils as utils

from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from r3make.commands import CBUILD_COMMANDS
from r3make.version import YEAR, MINOR, PATCH

from r3make.compiler import SUPPORTED_COMPILERS, BaseCompiler
from r3make.fetch import fetch_files, fetch_library, fetch_compiler_instance

def _build_summary(
        console:Console,
        c_instance,
        c_flags,
        c_defines,
        src_dirs,
        src_files,
        inc_dirs,
        lib_links,
        out_dir,
        out_type,
        out_name
        ) -> None:
    
    ver = f"{YEAR}.{MINOR}.{PATCH}"
    table = Table(title=f"Build Summary: {out_name}", caption=f"[bold green]r3make[/] [bold white]{ver}[/]", show_lines=True)
    table.add_column("Field", style="bold green", no_wrap=True)
    table.add_column("Value", style="bold cyan")
    table.add_row("Compiler", c_instance.name)
    table.add_row("Flags", " ".join(c_flags))
    table.add_row("Defines", " ".join(c_defines))
    table.add_row("Source Files", str(len(src_files)))
    table.add_row("Source Dirs", " ".join(src_dirs))
    table.add_row("Include Dirs", " ".join(inc_dirs))
    table.add_row("Libraries", " ".join(list(lib_links.keys())))
    table.add_row("Output Dir", out_dir)
    table.add_row("Output Type", out_type)
    
    console.print(table)

def r3make_build(console:Console, config) -> None:
    if not isinstance(config, dict): return None

    # extract compiler configuration
    c_instance:BaseCompiler = fetch_compiler_instance(config["c-instance"])
    if not isinstance(c_instance, BaseCompiler): return None
    
    c_flags = []
    c_defines = []
    if len(config["c-flags"]): 
        c_flags = [ c_flag.strip() for c_flag in config["c-flags"] ]
    if len(config["c-defines"]): 
        c_defines = [ c_define.strip() for c_define in config["c-defines"] ]

    # extract source file configuration
    src_dirs = []
    for src_dir in config["src-dirs"]:
        if not utils.os.path.exists(src_dir):
            print(f"Source Directory Not Found: {src_dir}")
            continue
        src_dirs.append(src_dir)
    
    src_files = []
    for src_dir in src_dirs:
        for src_file in fetch_files(".c", src_dir):
            src_files.append(src_file.strip())
    
    # extract include file configuration
    inc_dirs = []
    for inc_dir in config["inc-dirs"]:
        if not utils.os.path.exists(inc_dir):
            print(f"Include Directory Not Found: {inc_dir}")
            continue
        inc_dirs.append(inc_dir)
    
    # extract linked library configuration
    lib_links = {}
    if len(config["lib-links"]):
        for lib, path in config["lib-links"].items():
            if not path:
                lib_links[lib] = None
                continue
            if not utils.os.path.exists(path):
                print(f"Library ({lib}) Path Not Found: {path}")
                continue
            if fetch_library(lib, path):
                lib_links[lib] = path
    
    # extract output configuration
    out_dir = config["out-dir"]
    if not utils.os.path.exists(out_dir):
        utils.os_mkdir(out_dir)
    
    out_type = config["out-type"]
    if out_type not in c_instance.out_types:
        print(f"({c_instance.name}) Invalid Output Type: {out_type}")

    out_name = config["out-name"]

    # extract r3make commands
    pre_commands = config["r3make"]["pre-build"]
    post_commands = config["r3make"]["post-build"]
    for command in pre_commands:
        if command in CBUILD_COMMANDS:
            CBUILD_COMMANDS[command](config, param=pre_commands[command])

    _build_summary(
        console,
        c_instance,
        c_flags,
        c_defines,
        src_dirs,
        src_files,
        inc_dirs,
        lib_links,
        out_dir,
        out_type,
        out_name
    )

    # compile source code into object files
    if not utils.os.path.exists(f"{config["out-dir"]}{utils.SEP}ofiles"):
        try:
            utils.os.mkdir(f"{config["out-dir"]}{utils.SEP}ofiles")
        except Exception as e:
            print(e)
            return None

    ofiles:list[str] = c_instance.compile(
        c_flags,
        c_defines,
        src_files,
        inc_dirs,
        out_dir
    )

    # link object files into final output
    result:bool = c_instance.link(
        ofiles,
        lib_links,
        out_name,
        out_type,
        out_dir
    )

    for command in post_commands:
        if command in CBUILD_COMMANDS:
            CBUILD_COMMANDS[command](config, param=post_commands[command])

    if isinstance(result, Exception):
        console.print(Panel(f"[bold red]r3make[/] Build Failed", expand=False))
    elif isinstance(result, bool) and result == True:
        console.print(Panel(f"[bold green]r3make[/] Build Success", expand=False))
