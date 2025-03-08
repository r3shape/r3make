from argparse import ArgumentParser

from rich.panel import Panel
from rich.console import Console

from r3make.fetch import fetch_config, define_search_paths
from r3make.build import r3make_build
from r3make.config import parse_config
from r3make.version import YEAR, MINOR, PATCH

def main():
    console = Console()
    define_search_paths()
    parser = ArgumentParser(description="r3make - A lightweight C/C++ build tool")
    parser.add_argument('target', help="Specify the build target within the r3make configuration file")
    r3make_build(console, parse_config(fetch_config(), target=parser.parse_args().target))

if __name__ == "__main__":
    main()