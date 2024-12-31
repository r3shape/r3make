import os

SEP = os.path.sep

from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from cbuild.fetch import fetch_files, fetch_library, fetch_compiler_instance
from cbuild.compilers import SUPPORTED_COMPILERS, CompilerInstance, GCCCompiler, EMCCCompiler

def _rich_build_summary(console:Console, project:str, compiler:str, output:str, outdir:str, sources:list[str]) -> None:
    table = Table(title=f"Project Build Summary: {project}", show_lines=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_row("Compiler", compiler)
    table.add_row("Target Directory", outdir)
    table.add_row("Output Type", output)
    table.add_row("Source Files", f"{len(sources)} {"files" if len(sources) > 1 else "file"}")
    
    console.print(table)

def build_project(console:Console, config) -> None:
    if not isinstance(config, dict): return None

    # aquire the configured compiler instance
    cinstance:CompilerInstance = fetch_compiler_instance(config['compiler'])
    
    # validate configured include directories
    include_dirs = []
    if len(config["include_dirs"]):
        for include_dir in config["include_dirs"]:
            if not os.path.exists(include_dir):
                print(f"Include Directory Not Found: {include_dir}")
                return None
            else: include_dirs.append(include_dir)
    
    # validate configured library directories
    libraries = {}
    if len(config["libraries"]):
        for lib, path in config["libraries"].items():
            if not path:
                libraries[lib] = None
                continue
            if not os.path.exists(path):
                print(f"Library ({lib}) Path Not Found: {path}")
                return None
            if fetch_library(lib, path):
                libraries[lib] = path
        
    # validate configured output directory
    if not os.path.exists(config["output_dir"]):
        root = config["output_dir"].split(SEP)[0]
        dirs = config["output_dir"].split(SEP)[1:]
        os.mkdir(root)
        for d in dirs: os.mkdir(f"{root}{SEP}{d}")
    
    # collect all source files from all possible source fields
    source_files:str = ""
    if len(config["source_files"]):
        source_files += " ".join(config["source_files"])
    if len(config["source_dirs"]):
        for source_dir in config["source_dirs"]:
            source_files += " ".join(fetch_files(".c", source_dir)) + " "
    source_files = [*map(str.strip, source_files.split())]

    # set compiler flags
    [ cinstance.flags.append(flag) for flag in config["flags"] if len(config["flags"]) ]
    
    # collect defines
    compiler_defines = []
    [ compiler_defines.append(define) for define in config["defines"] if len(config["defines"]) ]
    
    # validate configured output type
    if config["output"] not in cinstance.outtypes:
        print(f"({cinstance.name}-Instance) Invalid Output Type: {config["output"]}")

    # create optional `ofiles` directory
    if not os.path.exists(f"{config["output_dir"]}{SEP}ofiles"):
        try:
            os.mkdir(f"{config["output_dir"]}{SEP}ofiles")
        except Exception as e:
            print(e)
            return None

    _rich_build_summary(
        console,
        config["project"],
        cinstance.name,
        config["output"],
        config["output_dir"],
        source_files,
    )

    # compile source code into object files
    ofiles:list[str] = cinstance.compile(
        console,
        compiler_defines,
        source_files,
        include_dirs,
        config["output_dir"]
    )

    # link object files into final output
    result:bool|Exception = cinstance.link(
        config["project"],
        config["output"],
        libraries,
        ofiles,
        config["output_dir"]
    )

    if isinstance(result, Exception):
        console.print(Panel(f"[bold red]CBUILD[/] Build Failed", expand=False))
    elif isinstance(result, bool) and result == True:
        console.print(Panel(f"[bold green]CBUILD[/] Build Success", expand=False))

