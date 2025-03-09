from rich.panel import Panel
from rich.console import Console

import r3make.utils as utils
from r3make.fetch import DEFAULT_SEARCH_PATHS

console = Console()
def _nofiles_command(config:dict, param=None) -> None:
    console.print(Panel(f"[bold cyan]nofiles[/] Removing O-Files", expand=False))
    utils.os.system(f"rmdir {config["out-dir"]}{utils.SEP}ofiles /s /q")
    console.print(Panel(f"[bold cyan]nofiles[/] Removed O-Files", expand=False))

def _gitdeps_command(config:dict, param=None) -> None:
    path = DEFAULT_SEARCH_PATHS["OS"][1] if utils.platform.system() == "Windows" else DEFAULT_SEARCH_PATHS["OS"][2]
    for dep in param:
        console.print(Panel(f"[bold cyan]gitdeps[/] Fetching Github Dependency ({dep})", expand=False))
        dep_name = dep.replace("/", utils.SEP).replace("\\", utils.SEP).split(utils.SEP)[1]
        try:
            cwd = utils.os.getcwd()
            # clone the dep
            if not utils.os.path.exists(f"{path}{utils.SEP}{dep_name}"):
                utils.os.mkdir(f"{path}{utils.SEP}{dep_name}")
                utils.os.system(f"git clone https://github.com/{dep}.git {path}{utils.SEP}{dep_name}")
            
            utils.os.chdir(f"{path}{utils.SEP}{dep_name}")
            
            # check if the .r3make directory exists
            if not utils.os.path.exists(".r3make"):
                console.print(Panel(f"[bold red]gitdeps[/] Dependency missing .r3make directory ({dep})", expand=False))
                utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)

            # extract output info to verify the desired build artifact was generated
            with open(f"r3make", "rb") as f:
                config = utils.json.load(f)
                f.close()

            target = config["c-targets"].get(f"{dep_name}")
            if not target:
                console.print(Panel(f"[bold red]gitdeps[/] Dependency missing repository compile-target ({dep})", expand=False))
                utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)
            
            out_dir = target.get("out-dir", False)
            out_type = target.get("out-type", False)
            out_name = target.get("out-name", False)

            if not all([out_dir, out_type, out_name]):
                console.print(Panel(f"[bold red]gitdeps[/] Dependency missing compile-target output configuration ({dep})", expand=False))
                utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)

            # check if this dependency is already built
            for r, d, f in utils.os.walk(f"{path}{utils.SEP}{dep_name}"):
                if utils.os_path(r).endswith(utils.os_path(out_dir)):
                    utils.os.chdir(f"{utils.os_path(r)}")
                    break
            
            if utils.os.path.exists(f"{out_name}.{out_type}"):
                console.print(Panel(f"[bold green]gitdeps[/] Dependency Already built ({dep})", expand=False))
                utils.os.chdir(cwd)
                continue
            else:
                # chdir into the .r3make directory and build the repository target
                utils.os.chdir(f"{path}{utils.SEP}{dep_name}{utils.SEP}.r3make")
                utils.os.system(f"r3make {dep_name}")
                
                for r, d, f in utils.os.walk(f"{path}{utils.SEP}{dep_name}"):
                    if utils.os_path(r).endswith(utils.os_path(out_dir)):
                        utils.os.chdir(f"{utils.os_path(r)}")
                        break
            
                if utils.os.path.exists(f"{out_name}.{out_type}"):
                    console.print(Panel(f"[bold green]gitdeps[/] Dependency built ({dep})", expand=False))
                    utils.os.chdir(cwd)
                    continue
                else:
                    console.print(Panel(f"[bold red]gitdeps[/] Fetched but failed to build dependency ({dep})", expand=False))
                    utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)
            utils.os.chdir(cwd)
            continue
        except (PermissionError):
            console.print(Panel(f"[bold red]gitdeps[/] Higher-Level Privilages Needed To Fetch Github Dependencies", expand=False))
            utils.os.kill(utils.os.getpid(), utils.signal.SIGBREAK)

    console.print(Panel(f"[bold cyan]gitdeps[/] Fetched Github Dependencies", expand=False))

CBUILD_COMMANDS:dict = {
    "nofiles": _nofiles_command,
    "gitdeps": _gitdeps_command,
}
