import argparse
from r3make.core import build_project
from r3make.util import log, load_config

def main():
    parser = argparse.ArgumentParser(description="r3make - JSON-based C build tool")
    parser.add_argument(
        "-f", "-F", "--file", "--File",
        default="r3make.json",
        help="Path to r3make config file (default: r3make.json)"
    )
    parser.add_argument(
        "-t", "-T", "--target", "--Target",
        default="main",
        help="Compilation target (default: main)"
    )
    parser.add_argument(
        "-v", "-V", "--verbose", "--Verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-nf", "-NF", "--nofiles", "--Nofiles", "--NoFiles",
        action="store_true",
        help="Delete object files after build"
    )
    parser.add_argument(
        "-be", "-BE", "--buildeach", "--Buildeach", "--BuildEach",
        action="store_true",
        help="Build each source file as its own target"
    )
    parser.add_argument(
        "-r", "-R", "--run", "--Run",
        action="store_true",
        help="Run an executable after building"
    )

    args = parser.parse_args()
    config = load_config(args.target, args.file)
    
    if config:
        build_project(
            config,
            args.target,
            run=args.run,
            verbose=args.verbose,
            clean_obj=args.nofiles,
            build_each=args.buildeach
        )
    else:
        log(f"Failed to load config: {args.target} {args.file}", "error")

