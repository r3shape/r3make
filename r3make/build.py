import r3make.utils as utils

from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from r3make.commands import CBUILD_COMMANDS
from r3make.version import YEAR, MINOR, PATCH

from r3make.compiler import SUPPORTED_COMPILERS, BaseCompiler
from r3make.fetch import fetch_files, fetch_library, fetch_compiler, fetch_compiler_instance

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

def r3make_build(console:Console, config: dict) -> None:
    if not isinstance(config, dict): return None

    # extract r3make config
    r3make_config = config.get("r3make", None)

    # extract compiler configuration
    if not fetch_compiler(config["c-instance"]):
        console.print(Panel(f"[bold red]r3make[/] Compiler not found on system: {config["c-instance"]}", expand=False))
        return None

    c_instance:BaseCompiler = fetch_compiler_instance(config["c-instance"])
    if not isinstance(c_instance, BaseCompiler):
        console.print(Panel(f"[bold red]r3make[/] Compiler not supported: {config["c-instance"]}", expand=False))
        return None
    
    c_flags = []
    c_defines = []
    if len(config["c-flags"]): 
        c_flags = [ c_flag.strip() for c_flag in config["c-flags"] ]
    if len(config["c-defines"]): 
        c_defines = [ c_define.strip() for c_define in config["c-defines"] ]

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
            if path == None:
                flib, fpath = fetch_library(lib, path)
                if fpath == "OS":
                    lib_links[flib] = None
                    continue
                elif fpath == None or not utils.os.path.exists(fpath):
                    print(f"Library Not Found: {flib}")
                    return
                lib_links[flib] = fpath
            elif utils.os.path.exists(path):
                for ext in ['.dll', '.a', '.lib', '.so']:
                    if f"{path}{utils.SEP}{lib}{ext}" in fetch_files(ext, path):
                        lib_links[lib] = path
                        break
                    else:
                        print(f"Library Not Found: {lib}")
                        return

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
    for file in config["src-files"]:
        if utils.os.path.exists(file):
            src_files.append(utils.os_path(file))
        else:
            print(f"unable to locate src file: {file}\n")
            return
        
    # extract output configuration
    out_dir = config["out-dir"]
    if not utils.os.path.exists(out_dir):
        utils.os_mkdir(out_dir)
    
    out_type = config["out-type"]
    if out_type not in c_instance.out_types:
        print(f"({c_instance.name}) Invalid Output Type: {out_type}")

    out_name = config["out-name"]
    
    # extract r3make pre-build commands
    if r3make_config:
        pre_commands = r3make_config["pre-build"]
        for command in pre_commands:
            if command in CBUILD_COMMANDS:
                CBUILD_COMMANDS[command](config, param=pre_commands[command])

    if not utils.os.path.exists(f"{config["out-dir"]}{utils.SEP}ofiles"):
        try:
            utils.os.mkdir(f"{config["out-dir"]}{utils.SEP}ofiles")
        except Exception as e:
            print(e)
            return None

    # show build summary
    _build_summary(console,
        c_instance, c_flags, c_defines,
        src_dirs, src_files, inc_dirs, lib_links,
        out_dir, out_type, out_name
    )

    # extract r3make flags
    # buildeach (builds each source file in the src-files field as a "subtarget" with the file name being the out-name of the subtarget)
    build_result = False
    single_target = True
    r3make_flags = r3make_config["flags"]
    for flag in r3make_flags:
        match flag.lower():
            case "buildeach":                                                       # `buildeach`` flag
                single_target = False
                for src in src_files:
                    out_name = src.removesuffix(".c").split(utils.SEP)[-1]
                    build_result = c_instance.link(
                        c_instance.compile(
                            c_flags, c_defines,
                            [src], inc_dirs, out_dir
                        ), lib_links, out_name,
                        out_type, out_dir
                    )
            case _: break

    if single_target:
        build_result = c_instance.link(
            c_instance.compile(
                c_flags, c_defines,
                src_files, inc_dirs, out_dir
            ), lib_links, out_name,
            out_type, out_dir
        )

    # extract r3make post-build commands
    if r3make_config:
        post_commands = r3make_config["post-build"]
        for command in post_commands:
            if command in CBUILD_COMMANDS:
                CBUILD_COMMANDS[command](config, param=post_commands[command])

    # indicate build result
    if build_result == False: console.print(Panel(f"[bold red]r3make[/] Build Failed", expand=False))
    elif build_result == True: console.print(Panel(f"[bold green]r3make[/] Build Success", expand=False))
