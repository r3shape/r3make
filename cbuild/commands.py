from rich.panel import Panel
from rich.console import Console

import cbuild.utils as utils

console = Console()
def _test_command(config:dict, param=None) -> None:
    console.print(Panel(f"[bold cyan]cbuild command[/] {param}", expand=False))

def _nofiles_command(config:dict, param=None) -> None:
    console.print(Panel(f"[bold cyan]cbuild command[/] Removing O-Files", expand=False))
    utils.os.system(f"rmdir {config["out-dir"]}{utils.SEP}ofiles /s /q")
    console.print(Panel(f"[bold cyan]cbuild command[/] Removed O-Files", expand=False))

CBUILD_COMMANDS:dict = {
    "nofiles": _nofiles_command,
    "print-test": _test_command
}
