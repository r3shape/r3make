import argparse
from r3make.core import build_project
from r3make.util import log, load_config

def main():
    parser = argparse.ArgumentParser(description="r3make - JSON-based C build tool")
    parser.add_argument(
        "-f", "--file",
        default="r3make.json",
        help="Path to r3make config file (default: r3make.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()

    config = load_config(args.file)
    build_project(config, verbose=args.verbose)
