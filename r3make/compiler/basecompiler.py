from rich.console import Console
from rich.progress import Progress, BarColumn, SpinnerColumn

import r3make.utils as utils

class BaseCompiler:
    def __init__(
            self,
            name:str,
            prefix:str,
            out_types:list = []
        ):
        self.name:str = name
        self.prefix:str = prefix
        self.out_types:list = out_types

    def compile(self, c_flags: list, c_defines: list, src_files: list[str], inc_dirs: list[str], out_dir: str) -> list[str]:
        ofiles = []
        with Progress(SpinnerColumn(), "[progress.description]{task.description}", BarColumn(), transient=True) as progress:
            for source in progress.track(src_files, description=f"Compiling {self.name} source files..."):
                sourcefile = source.split(utils.SEP)[-1].replace(".c", ".o")
                ofile = f"{out_dir}{utils.SEP}ofiles{utils.SEP}{sourcefile}"
                
                flag_str = " ".join([f"{flag.strip()}" for flag in c_flags])
                define_str = " ".join([f"-D{define.strip()}" for define in c_defines])
                include_str = " ".join([f"-I{include.strip()}" for include in inc_dirs])

                command = f"{self.prefix} {flag_str} {define_str} {include_str} -c {source} -o {ofile}"
                try:
                    utils.subprocess.run(command, check=True)
                    ofiles.append(ofile)
                except FileNotFoundError:
                    utils.os.system(command)
                    ofiles.append(ofile)
                except (OSError, utils.subprocess.CalledProcessError) as e:
                    print(f"Error during Compile: {e}")
                    return None
        return ofiles

    def link(self, ofiles: list[str], lib_links: dict[str, str], out_name: str, out_type: str, out_dir: str) -> bool:
        ofile_str = " ".join(ofiles)
        lib_str = " ".join([f"-l{lib}" for lib in lib_links])
        lib_dir_str = " ".join([f"-L{lib_links[lib]}" for lib in lib_links if lib_links[lib] != None])

        out_ext = f".{out_type}" if out_type in self.out_types else ""

        platform_name = utils.platform.system().lower()
        if out_type in ["dll", "so", "dylib"]:
            if platform_name == "darwin":
                command = f"{self.prefix} -dynamiclib {ofile_str} {lib_str} {lib_dir_str} -o {out_dir}{utils.SEP}{out_name}{out_ext}"
            else:
                command = f"{self.prefix} -shared {ofile_str} {lib_str} {lib_dir_str} -o {out_dir}{utils.SEP}{out_name}{out_ext}"

        elif out_type == "exe":
            command = f"{self.prefix} {ofile_str} {lib_str} {lib_dir_str} -o {out_dir}{utils.SEP}{out_name}{out_ext}"

        try:
            utils.subprocess.run(command, check=True)
            return True
        except FileNotFoundError:
            utils.os.system(command)
            return True
        except (OSError, utils.subprocess.CalledProcessError) as e:
            print(f"Error during Linking: {e}")
            return False
