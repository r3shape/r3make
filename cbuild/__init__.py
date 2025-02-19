from argparse import ArgumentParser

from rich.panel import Panel
from rich.console import Console

from cbuild.build import cbuild_build
from cbuild.config import parse_config
from cbuild.version import YEAR, MINOR, PATCH

def main():
    console = Console()
    parser = ArgumentParser(description="cbuild - A Simple C Build Tool")
    parser.add_argument('config', help="Path to the .cbuild configuration file")
    cbuild_build(console, parse_config(parser.parse_args().config))

if __name__ == "__main__":
    main()