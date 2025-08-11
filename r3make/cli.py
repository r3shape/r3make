import argparse
from r3make.core import build_project
from r3make.util import log, load_config

# import cli commands
from r3make.cmd.gitdeps import gitdeps
from r3make.cmd.clangdcmd import clangdcmd

def cli_arg(parser: argparse.ArgumentParser, shorthand: str, name: str, default: str=None, help: str=None, store_true: bool=False):
    if store_true:
        parser.add_argument(
            f"-{shorthand.lower()}", f"-{shorthand.capitalize()}", f"--{name.lower()}", f"--{name.capitalize()}",
            action="store_true",
            default=default,
            help=help
            
        )
    else:
        parser.add_argument(
            f"-{shorthand.lower()}", f"-{shorthand.capitalize()}", f"--{name.lower()}", f"--{name.capitalize()}",
            default=default,
            help=help
            
        )

def main():
    parser = argparse.ArgumentParser(description="r3make - JSON-based C build tool")
    cli_arg(
        parser,
        "t", "target",
        default="main",
        help="Compilation target (default: main)",
    )
    cli_arg(
        parser,
        "v", "verbose", store_true=True,
        help="Enable verbose output",
    )
    cli_arg(
        parser,
        "nf", "noFiles", store_true=True,
        help="Delete object files after build",
    )
    cli_arg(
        parser,
        "be", "buildEach", store_true=True,
        help="Build each source file as its own target",
    )
    cli_arg(
        parser,
        "r", "run", store_true=True,
        help="Run an executable after building",
    )
    cli_arg(
        parser,
        "ccmd", "clangdCmd", store_true=True,
        help="Generate clangd LSP compilation configuration. (for vim/neovim users)",

    )

    args = parser.parse_args()
    config = load_config(args.target, "r3make.json")

    if config:
        gitdeps(args.target, config, verbose=args.verbose)
        build_project(
            main_config=config,
            target=args.target,
            run=args.run,
            verbose=args.verbose,
            nofiles=args.nofiles,
            buildeach=args.buildeach,
            clangdcmd=args.clangdcmd
        )
        if args.clangdcmd:
            if not clangdcmd(config, "./r3make.json"):
                log("Failed to generate clangd LSP 'compile_commands.json'", "error")
            else:
                log("Generated clangd LSP 'compile_commands.json'", "success")
    else:
        log(f"Failed to load config: {args.target} {args.file}")
        exit(1)
