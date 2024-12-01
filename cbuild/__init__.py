from argparse import ArgumentParser

from rich.panel import Panel
from rich.console import Console

from cbuild.config import parse_config
from cbuild.build import build_project
from cbuild.version import YEAR, MINOR, PATCH

def main():
    console = Console()
    console.print(Panel(f"[bold green]CBUILD[/] {YEAR}.{MINOR}.{PATCH}", expand=False))

    parser = ArgumentParser(description="CBUILD - A Simple C Build Tool")
    parser.add_argument('config', help="Path to the .cbuild configuration file")
    build_project(console, parse_config(parser.parse_args().config))

if __name__ == "__main__":
    main()