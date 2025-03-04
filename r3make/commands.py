from rich.panel import Panel
from rich.console import Console

import r3make.utils as utils
from r3make.fetch import DEFAULT_SEARCH_PATHS

console = Console()
def _nofiles_command(config:dict, param=None) -> None:
    console.print(Panel(f"[bold cyan]r3make command[/] Removing O-Files", expand=False))
    utils.os.system(f"rmdir {config["out-dir"]}{utils.SEP}ofiles /s /q")
    console.print(Panel(f"[bold cyan]r3make command[/] Removed O-Files", expand=False))

def _gitdeps_command(config:dict, param=None) -> None:
    console.print(Panel(f"[bold cyan]r3make command[/] Fetching Github Dependencies", expand=False))
    path = DEFAULT_SEARCH_PATHS["OS"][1] if utils.platform.system() == "Windows" else DEFAULT_SEARCH_PATHS["OS"][2]
    for dep in param:
        dep_name = dep.replace("/", utils.SEP).replace("\\", utils.SEP).split(utils.SEP)[1]
        try:
            cwd = utils.os.getcwd()
            if not utils.os.path.exists(f"{path}{utils.SEP}{dep_name}"): utils.os.mkdir(f"{path}{utils.SEP}{dep_name}")
            else:
                # this dep already exists at this path!
                # but check if its built
                utils.os.chdir(f"{path}{utils.SEP}{dep_name}")

                if not utils.os.path.exists(".r3make"):
                    console.print(Panel(f"[bold red]r3make command[/] Dependency missing .r3make directory ({dep})", expand=False))
                    utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)

                with open(f".r3make{utils.SEP}{dep_name}.r3make", "rb") as f:
                    config = utils.json.load(f)
                    f.close()

                out_dir = config["out-dir"]
                out_type = config["out-type"]
                out_name = config["out-name"]
                if utils.os.path.exists(f"{utils.os_path(out_dir)}{utils.SEP}{out_name}.{out_type}"):
                    console.print(Panel(f"[bold green]r3make command[/] Fetched and built ({dep})", expand=False))
                else:   # try building the dep again
                    utils.os.system(f"r3make .r3make{utils.SEP}{dep_name}.r3make")
                
                    if utils.os.path.exists(f"{utils.os_path(out_dir)}{utils.SEP}{out_name}.{out_type}"):
                        console.print(Panel(f"[bold green]r3make command[/] Fetched and built ({dep})", expand=False))
                    else:
                        console.print(Panel(f"[bold red]r3make command[/] Fetched but failed to build dependency ({dep})", expand=False))
                        utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)
                utils.os.chdir(cwd)
                continue

            utils.os.system(f"git clone https://github.com/{dep}.git {path}{utils.SEP}{dep_name}")

            utils.os.chdir(f"{path}{utils.SEP}{dep_name}")

            if not utils.os.path.exists(".r3make"):
                console.print(Panel(f"[bold red]r3make command[/] Dependency missing .r3make directory ({dep})", expand=False))
                utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)
            else:
                console.print(Panel(f"[bold cyan]r3make command[/] Building dependency ({dep})", expand=False))

            utils.os.system(f"r3make .r3make{utils.SEP}{dep_name}.r3make")

            with open(f".r3make{utils.SEP}{dep_name}.r3make", "rb") as f:
                config = utils.json.load(f)
                f.close()

            out_dir = config["out-dir"]
            out_type = config["out-type"]
            out_name = config["out-name"]
            if utils.os.path.exists(f"{utils.os_path(out_dir)}{utils.SEP}{out_name}.{out_type}"):
                console.print(Panel(f"[bold green]r3make command[/] Fetched and built ({dep})", expand=False))
            else:
                console.print(Panel(f"[bold red]r3make command[/] Fetched but failed to build dependency ({dep})", expand=False))
                utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)
            utils.os.chdir(cwd)
        except (PermissionError):
            console.print(Panel(f"[bold red]r3make command[/] Higher-Level Privilages Needed To Fetch Github Dependencies", expand=False))
            utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)

    console.print(Panel(f"[bold cyan]r3make command[/] Fetched Github Dependencies", expand=False))

CBUILD_COMMANDS:dict = {
    "nofiles": _nofiles_command,
    "gitdeps": _gitdeps_command,
}
