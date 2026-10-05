import os
import sys
import glob
import json
import shutil
import argparse
import platform
import subprocess
from pathlib import Path

class R3BuildTarget:
    def __init__(self, data: dict) -> None:
        self.objs: list[str] = []

        self.type: str = data.get("type")
        self.dest: str = data.get("dest")
        self.sources: list[str] = data.get("sources")

        self.artifact: str = {
            "dll": ".dll" if platform.system() == "Windows" else ".so",
            "lib": ".lib" if platform.system() == "Windows" else ".a",
            "exe": ".exe" if platform.system() == "Windows" else "",
        }[self.type]

        self.name: str = data.get("name", None)
        self.deps: list[str] = data.get("deps", [])
        self.ccflags: list[str] = data.get("ccflags", [])
        self.ldflags: list[str] = data.get("ldflags", [])
        self.defines: list[str] = data.get("defines", [])
        self.includes: list[str] = data.get("includes", [])
        self.requires: list[str] = data.get("requires", [])

    def getCCFlags(self) -> list[str]:
        return [f"-{flag}" if not flag.startswith('-') else flag for flag in self.ccflags]

    def getLDFlags(self) -> list[str]:
        return [f"-{flag}" if not flag.startswith('-') else flag for flag in self.ldflags]

    def getIncludes(self) -> list[str]:
        return [f"-I{path}" for path in self.includes]

    def getDefines(self) -> list[str]: 
        return [f"-D{define}" for define in self.defines]

class R3Make:
    VERBOSE: int = 1 << 0
    MULTI: int = 1 << 1
    CLEAN: int = 1 << 2
    DUMP: int = 1 << 3
    RUN: int = 1 << 4

    HOME_DIR: str = os.path.expanduser("~")
    GHREPO_DIR: str = os.path.join(HOME_DIR, "r3make", "deps", "github", "user", "repo")

    def __init__(self) -> None:
        self.mask: int = 0
        self.root: str = '.'
        self.r3make: dict = {}
        self.commands: list = []
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser()

    @property
    def verbose(self) -> bool: return self.mask & self.VERBOSE
    @property
    def multi(self) -> bool: return self.mask & self.MULTI
    @property
    def clean(self) -> bool: return self.mask & self.CLEAN
    @property
    def dump(self) -> bool: return self.mask & self.DUMP
    @property
    def run(self) -> bool: return self.mask & self.RUN

    def log(self, msg: str, kind :str="info"):
        print(f"[r3make {kind}] {msg}", flush=True)


    def getCompiler(self) -> str:
        for comp in ["gcc", "clang", "cl"]:
            if shutil.which(comp):
                return comp
        return

    def getGlob(self, files: list[str], ext: str):
        expanded = []
        for pattern in files:
            expanded += glob.glob(pattern, recursive=True)
        return [file for file in expanded if file.endswith(ext)]


    def handleGitHub(self, repo: str, target: R3BuildTarget) -> None:
        root = self.GHREPO_DIR
        path = os.path.join(root, repo)
        path = os.path.join(path, self.root)
        
        cmd = ["git", "clone", f"https://github.com/{repo}.git", path]
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if subprocess.call(cmd) != 0:
                self.log(f"dep clone failed: {repo}", "error")
                return

        # capture local state
        cwd = os.getcwd()
        r3makeOld = self.r3make

        try:
            os.chdir(path)
            with open(os.path.join(path, "r3make.json"), "r") as file:
                r3makeNew = json.load(file)    
        except FileNotFoundError:
            self.log(f"r3make.json not found for remote dependency: {repo}", "error")
            return
        finally: os.chdir(cwd)

        dep = R3BuildTarget(r3makeNew["main"])
        artifact = os.path.join(path, dep.dest, dep.name + dep.artifact)
        if not os.path.exists(artifact):
            try:
                # update local state to remote state
                os.chdir(path)
                self.r3make = r3makeNew
                build = self.build()
            finally:
                # restore local state
                self.r3make = r3makeOld
                os.chdir(cwd)
            if not build:
                self.log(f"failed building remote dependency: {repo}", "error")
                return
        else: build = dep

        target.ldflags.append(f"-L{os.path.join(path, dep.dest)}")
        target.ldflags.append(f"-l{dep.name}")

    def handleDest(self, target: R3BuildTarget) -> None:
        if target.dest[0] == '@':
            if target.dest[1:] not in self.r3make:
                self.log(f"target not found: {target.dest[1:]}", "error")
                return False
            target.dest = self.r3make[target.dest[1:]]["dest"]

        if not os.path.exists(target.dest):
            os.makedirs(target.dest, exist_ok=True)

    def handleFlags(self, target: R3BuildTarget) -> None:
        ccflags = []
        for flag in target.ccflags:
            if flag[0] == '@':
                if flag[1:] not in self.r3make:
                    self.log(f"required flag not found: {flag[1:]}", "error")
                    return False
                ccflags.extend(self.r3make[flag[1:]]["ccflags"])
            else:
                ccflags.append(flag)
        target.ccflags = ccflags

        ldflags = []
        for flag in target.ldflags:
            if flag[0] == '@':
                if flag[1:] not in self.r3make:
                    self.log(f"required flag not found: {flag[1:]}", "error")
                    return False
                ldflags.extend(self.r3make[flag[1:]]["ldflags"])
            else:
                ldflags.append(flag)
        target.ldflags = ldflags

    def handleSources(self, target: R3BuildTarget) -> None:
        for path in target.sources:
            if not os.path.exists(path):
                self.log(f"source path not found: {path}", "error")
                return False

    def handleIncludes(self, target: R3BuildTarget) -> None:
        includes = []
        for i,path in enumerate(target.includes):
            if path[0] != '@' and not os.path.exists(path):
                self.log(f"include path not found: {path}", "error")
                return False

            if path[0] == '@':
                path = path[1:]
                if path not in self.r3make:
                    self.log(f"required include not found: {path}", "error")
                    return False
                
                includes.extend(target.includes[:i])
                includes.extend(target.includes[i+1:])

                req = self.r3make[path]["includes"]
                for inc in req:
                    if inc[0] != '@' and not os.path.exists(inc):
                        self.log(f"required include not found: {inc}", "error")
                        return False
                includes.extend(self.r3make[path]["includes"])

            else: includes.append(path)
        target.includes = includes

    def handleRequires(self, target: R3BuildTarget) -> None:
        for req in target.requires:
            if req[0] == '@':
                if req[1:] not in self.r3make:
                    self.log(f"required target not found: {req[1:]}", "error")
                    return False
                req = self.r3make[req[1:]]["requires"]
            else:
                if req not in self.r3make:
                    self.log(f"required target not found: {req}", "error")
                    return False
            
            if not (build := self.build(req)):
                self.log(f"failed making required target: {req}", "error")
                return False
            target.deps.append(f"{build.dest}:{build.name}")

    def handleDependencies(self, target: R3BuildTarget) -> None:
        deps = []
        for dep in target.deps:
            if dep[0] == '@':
                if dep[1:] not in self.r3make:
                    self.log(f"required dependency not found: {dep[1:]}", "error")
                    return False
                deps.extend(self.r3make[dep[1:]].get("deps", []))
            else:
                deps.append(dep)

        target.deps = deps
        for dep in target.deps:
            prefix,suffix = dep.split(":")
            if prefix == "github":
                self.handleGitHub(suffix, target)
            else:
                if prefix != '~' and not os.path.exists(prefix):
                    self.log(f"CWD{os.getcwd()}| dep {dep} path not found: {prefix}", "error")
                    return False
                target.ldflags.append(f"-l{suffix}")
                if prefix != '~':
                    target.ldflags.append(f"-L{prefix}")


    def comp(self, comp: str, target: R3BuildTarget, sources: list[str]|None=None) -> None:
        base = [comp]
        base.extend(target.getCCFlags())
        base.extend(target.getDefines())
        base.extend(target.getIncludes())

        sources = sources if sources is not None else self.getGlob(target.sources, ".c")
        for src in sources:
            obj = os.path.join(target.dest, Path(src).stem + ".o")
            cmd = [*base, "-c", src, "-o", obj]

            if self.verbose: 
                self.log(f"compiling: {src} | {cmd}", "info")
            
            if self.dump:
                dump = {
                    "command": " ".join(cmd),
                    "directory":os.getcwd(),
                    "file": src,
                }
                if dump not in self.commands:
                    self.commands.append(dump)
            if subprocess.call(cmd) == 0:
                target.objs.append(obj)
                if self.verbose: 
                    self.log(f"compiled: {src}", "info")
            else:
                self.log(f"compilation failed: {src}", "error")

    def link(self, comp: str, target: R3BuildTarget, out: str|None=None) -> bool:
        out = os.path.join(target.dest, (out if out else target.name) + target.artifact)
        match target.type:
            case "lib"|"static": 
                cmd = ["ar", "rcs", out, *target.objs]
                if self.verbose: self.log(f"linking: {cmd}", "info")
                return subprocess.call(cmd) == 0
            case "exe"|"executable":
                cmd = [comp, *target.objs, *target.getLDFlags(), "-o", out]
                if self.verbose: self.log(f"linking: {cmd}", "info")
                return subprocess.call(cmd) == 0
            case "so"|"dll"|"shared"|"dynamic":
                cmd = [comp, "-shared", *target.objs, *target.getLDFlags(), "-o", out]
                if self.verbose: self.log(f"linking: {cmd}", "info")
                return subprocess.call(cmd) == 0
    
    def build(self, t: str="main") -> R3BuildTarget|None:
        os.chdir(self.root)

        if t not in self.r3make:
            self.log(f"target not found: {t}", "error")
            return None
        
        target = R3BuildTarget(self.r3make[t])
        if target.name is None: target.name = t

        if self.verbose:
            self.log(f"making: {target.name}", "info")

        comp = self.getCompiler()
        if comp is None:
            self.log("no compiler found.", "error")
            return

        if self.dump:
            try:
                with open("compile_commands.json", "r") as f:
                    self.commands = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        self.handleDest(target)
        self.handleFlags(target)
        self.handleSources(target)
        self.handleIncludes(target)
        self.handleRequires(target)
        self.handleDependencies(target)

        if not self.multi:
            self.comp(comp, target)
            if not self.link(comp, target): return
        else:
            objs = []
            for src in self.getGlob(target.sources, ".c"):
                self.comp(comp, target, [src])
                if not self.link(comp, target, Path(src).stem): return
                objs.extend(target.objs)
                target.objs.clear()
            target.objs = objs
        if self.clean:
            for obj in target.objs:
                if os.path.exists(obj):
                    os.remove(obj)

        if self.run and target.type in ["exe", "executable"]:
            artifact = os.path.join(target.dest, target.name + target.artifact)
            if os.path.exists(artifact): subprocess.run([artifact])

        if self.dump:
            try:
                with open("compile_commands.json", "w") as f:
                    json.dump(self.commands, f, indent=4)
            except IOError: self.log("command dump failed", "error")

        self.log(f"made: {target.name} @ {target.dest}", "info")
        return target


    def newArg(
        self,
        name: str,
        short: str,
        help: str=None,
        default: str=None,
        nargs: int = None,
        empty: bool=False,
        required: bool = False) -> None:
        if empty:
            self.parser.add_argument(
                f"-{short.lower()}", f"-{short.capitalize()}", f"--{name.lower()}", f"--{name.capitalize()}",
                action="store_true",
                required=required,
                default=default,
                help=help
            )
        else:
            self.parser.add_argument(
                *[f"-{short.lower()}", f"-{short.capitalize()}", f"--{name.lower()}", f"--{name.capitalize()}"],
                required=required,
                default=default,
                nargs=nargs,
                help=help
            )

    def main(self) -> None:
        self.newArg("target", "t")
        self.newArg("run", "r", empty=True)
        self.newArg("dump", "d", empty=True)
        self.newArg("multi", "m", empty=True)
        self.newArg("clean", "c", empty=True)
        self.newArg("verbose", "v", empty=True)

        args = self.parser.parse_args()
        if args.verbose: self.mask |= self.VERBOSE
        if args.multi: self.mask |= self.MULTI
        if args.clean: self.mask |= self.CLEAN
        if args.dump: self.mask |= self.DUMP
        if args.run: self.mask |= self.RUN

        try:
            with open("./r3make.json", "r") as file:
                self.r3make = json.load(file)
        except FileNotFoundError:
            self.log("r3make.json not found.", "error")
            return

        if not os.path.exists(self.GHREPO_DIR):
            os.makedirs(self.GHREPO_DIR, exist_ok=True)

        self.root = self.r3make.get("root", '.')
        target = args.target if args.target else "main"
        if target == "all":
            for t in self.r3make.get("all", []):
                self.build(t)
        else: self.build(target)


def main() -> None:
    r3make = R3Make()
    r3make.main()

if __name__ == "__main__":
    main()