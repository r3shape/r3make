import os
import sys
import glob
import json
import shutil
import argparse
import platform
import subprocess
from pathlib import Path

from r3make import target
from r3make.project import R3Project
from r3make.target import R3BuildTarget
from r3make.reference import R3Reference

class R3Make:
    VERSION: str = "2026.1.1"

    VERBOSE: int = 1 << 0
    MULTI: int = 1 << 1
    CLEAN: int = 1 << 2
    DUMP: int = 1 << 3
    RUN: int = 1 << 4

    HOME_DIR: str = os.path.expanduser("~")
    PROJECT_DIR: str = os.path.join(HOME_DIR, "r3make", "projects")
    PROJECTS: str = os.path.join(HOME_DIR, "r3make", "projects.json")
    REMOTE_DIR: str = os.path.join(HOME_DIR, "r3make", "deps", "github", "user", "repo")

    def __init__(self) -> None:
        self.mask: int = 0
        self.root: str = '.'
        self.r3make: dict = {}
        self.projects: dict = {}
        self.commands: list = []
        self.project: R3Project = None
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

    def getRef(self, ref: str) -> R3Reference:
        if "::" in ref:
            name,target = ref.split("::", 1)
            if name not in self.projects:
                self.log(f"project not found: {name}", "error")
                self.log(f"unable to resolve reference: @{ref}", "error")
                sys.exit(1)
            
            projectPath = self.projects[name]
            if not os.path.exists(projectPath):
                self.log(f"project not found: {name} @ {projectPath}", "error")
                self.log(f"unable to resolve reference: @{ref}", "error")
                sys.exit(1)

            with open(projectPath, "r") as f:
                data = json.load(f)
            with open(os.path.join(data["path"], "r3make.json"), "r") as f:
                projectData = json.load(f)
            project = R3Project(projectData, data["path"])

            if target not in project.targets:
                self.log(f"target not found in project: {target}", "error")
                self.log(f"unable to resolve reference: @{ref}", "error")
                sys.exit(1)
            return R3Reference(project, R3BuildTarget(target, projectData[target]))

        if ref not in self.r3make:
            self.log(f"target not found: {ref}", "error")
            self.log(f"unable to resolve reference: @{ref}", "error")
            sys.exit(1)
        return R3Reference(self.project, R3BuildTarget(ref, self.r3make[ref]))


    def handleGitHub(self, repo: str, ref: R3Reference) -> None:
        root = self.REMOTE_DIR
        path = os.path.join(root, repo)
        path = os.path.join(path, self.root)
        cmd = ["git", "clone", f"https://github.com/{repo}.git", path]
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if subprocess.call(cmd) != 0:
                self.log(f"dep clone failed: {repo}", "error")
                return
        try:
            with open(os.path.join(path, "r3make.json"), "r") as file:
                r3make = json.load(file)
        except FileNotFoundError:
            self.log(f"r3make.json not found for remote dependency: {repo}", "error")
            return
        project = R3Project(r3make, path)
        dep = R3Reference(project, R3BuildTarget("main", r3make["main"]))
        if not os.path.exists(dep.getArtifactPath()):
            if not self.build(dep):
                self.log(f"failed building remote dependency: {repo}", "error")
                return
        ref.target.ldflags.append(f"-l{dep.target.name}")
        ref.target.ldflags.append(f"-L{os.path.join(path, dep.target.dest)}")

    def handleDest(self, ref: R3Reference) -> None:
        if ref.target.dest[0] == '@':
            ref.target.dest = self.getRef(ref.target.dest[1:]).target.dest

        if not os.path.exists(ref.target.dest):
            os.makedirs(ref.target.dest, exist_ok=True)


    def resolveCCFlags(self, ref: R3Reference) -> list[str]:
        out = []
        for flag in ref.target.ccflags:
            if flag[0] == '@':
                child = self.getRef(flag[1:])
                if child.project.name == ref.project.name\
                and ref.target.target in flag: continue
                out.extend(self.resolveCCFlags(child))
            else:
                out.append(flag)
        return out

    def resolveLDFlags(self, ref: R3Reference) -> list[str]:
        out = []
        for flag in ref.target.ldflags:
            if flag[0] == '@':
                child = self.getRef(flag[1:])
                if child.project.name == ref.project.name\
                and ref.target.target in flag: continue
                out.extend(self.resolveLDFlags(child)) 
            else: 
                out.append(flag) 
        return out

    def handleFlags(self, ref: R3Reference) -> None:
        ref.target.ccflags = self.resolveCCFlags(ref)
        ref.target.ldflags = self.resolveLDFlags(ref)


    def handleSources(self, ref: R3Reference) -> None:
        for path in ref.target.sources:
            if not os.path.exists(path):
                self.log(f"source path not found: {path}", "error")
                return

    
    def resolveIncludes(self, ref: R3Reference) -> list[str]:
        out = []
        for inc in ref.target.includes:
            if inc[0] == '@':
                child = self.getRef(inc[1:])
                if child.project.name == ref.project.name\
                and ref.target.target in inc: continue
                out.extend(self.resolveIncludes(child))
            else: out.append(os.path.join(ref.path, inc))
        return out

    def handleIncludes(self, ref: R3Reference) -> None:
        ref.target.includes = self.resolveIncludes(ref)
        for include in ref.target.includes:
            if not os.path.exists(include):
                self.log(f"include path not found: {include}", "error")
                return


    def handleRequires(self, ref: R3Reference) -> None:
        target = ref.target
        for req in target.requires:
            if req[0] == '@':
                required = self.getRef(req[1:])
            else: required = self.getRef(req)
            if ref.project.name == required.project.name\
            and target.target in req: continue

            if not (build := self.build(required)):
                self.log(f"failed making required target: {required.target.name}", "error")
                return
            target.deps.append(build.getArtifactDir()+"::"+build.target.name)
            target.includes.extend(build.target.includes)


    def resolveDependencies(self, ref: R3Reference) -> list[str]:
        out = []
        for dep in ref.target.deps:
            if dep[0] == '@':
                if ref.target.target in dep: continue
                child = self.getRef(dep[1:])
                if child.project.name == ref.project.name\
                and ref.target.target in dep: continue
                if not os.path.exists(child.getArtifactPath()):
                    if not self.build(child):
                        self.log(f"dependency failed to build: {child.target.name}", "error")
                        sys.exit(1)
                out.append(child.getArtifactDir()+"::"+child.target.name)
                out.extend(self.resolveDependencies(child))
            else:
                prefix, suffix = dep.split("::")
                if prefix not in ['~', "github"]:
                    prefix = os.path.join(ref.path, prefix)
                out.append(prefix+"::"+suffix)
        return out
    
    def handleDependencies(self, ref: R3Reference) -> None:
        ref.target.deps = self.resolveDependencies(ref)
        for dep in ref.target.deps:
            prefix,suffix = dep.split("::")
            if prefix == "github":
                self.handleGitHub(suffix, ref)
            else:
                if prefix != '~' and not os.path.exists(prefix):
                    self.log(f"CWD ({os.getcwd()})| dep {dep} path not found: {prefix}", "error")
                    return
                ref.target.ldflags.append(f"-l{suffix}")
                if prefix != '~':
                    ref.target.ldflags.append(f"-L{prefix}")


    def comp(self, comp: str, ref: R3Reference, sources: list[str]|None=None) -> None:
        base = [comp]
        base.extend(ref.target.getCCFlags())
        base.extend(ref.target.getDefines())
        base.extend(ref.target.getIncludes())

        sources = sources if sources is not None else self.getGlob(ref.target.sources, ".c")
        for src in sources:
            obj = os.path.join(ref.target.dest, Path(src).stem + ".o")
            cmd = [*base, "-c", src, "-o", obj]

            if self.verbose: 
                self.log(f"compiling: {" ".join(cmd)}", "info")
            
            if self.dump:
                dump = {
                    "command": " ".join(cmd),
                    "directory":os.getcwd(),
                    "file": src,
                }
                if dump not in self.commands:
                    self.commands.append(dump)
            if subprocess.call(cmd) == 0:
                ref.target.objs.append(obj)
                if self.verbose: 
                    self.log(f"compiled: {src}", "info")
            else:
                self.log(f"compilation failed: {src}", "error")

    def link(self, comp: str, ref: R3Reference, out: str|None=None) -> bool:
        out = os.path.join(ref.target.dest, (out if out else ref.target.name) + ref.target.artifact)
        if ref.target.type in ["lib","static"]:
            cmd = ["ar", "rcs", out, *ref.target.objs]
            if self.verbose: self.log(f"linking: {" ".join(cmd)}", "info")
            return subprocess.call(cmd) == 0
        if ref.target.type in ["exe","executable"]:
            cmd = [comp, *ref.target.objs, *ref.target.getLDFlags(), "-o", out]
            if self.verbose: self.log(f"linking: {" ".join(cmd)}", "info")
            return subprocess.call(cmd) == 0
        if ref.target.type in ["so","dll","shared","dynamic"]:
            cmd = [comp, "-shared", *ref.target.objs, *ref.target.getLDFlags(), "-o", out]
            if self.verbose: self.log(f"linking: {" ".join(cmd)}", "info")
            return subprocess.call(cmd) == 0
    
    def build(self, ref: R3Reference) -> R3Reference|None:
        cwd = os.getcwd()
        if not os.path.exists(ref.path):
            self.log(f"project path does not exist: {ref.path}", "error")
            return
        try:
            os.chdir(ref.path)

            target = ref.target
            if target.name is None: target.name = target.target

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

            self.handleDest(ref)
            self.handleFlags(ref)
            self.handleSources(ref)
            self.handleIncludes(ref)
            self.handleRequires(ref)
            self.handleDependencies(ref)

            if not self.multi:
                self.comp(comp, ref)
                if not self.link(comp, ref): return
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
                artifact = target.getArtifactPath()
                if os.path.exists(artifact): subprocess.run([artifact])

            if self.dump:
                try:
                    with open("compile_commands.json", "w") as f:
                        json.dump(self.commands, f, indent=4)
                except IOError: self.log("command dump failed", "error")

            self.log(f"made: {target.name} @ {target.dest}", "info")
            return R3Reference(ref.project, target)
        finally: os.chdir(cwd)


    def listProjects(self) -> None:
        rem = []
        self.log("stored projects", "info")
        for name, path in self.projects.items():
            if not os.path.exists(path):
                self.log(f"project not found: {name} @ {path}", "error")
                rem.append(name)
                continue

            with open(self.projects[name], "r") as f:
                data = json.load(f)
            r3makePath = os.path.join(data["path"], "r3make.json")

            if not os.path.exists(r3makePath):
                self.log(f"r3make.json not found for project: {name} @ {r3makePath}", "error")
                rem.append(name)
                continue

            with open(r3makePath, "r") as f:
                projectData = json.load(f)
            project = R3Project(projectData, data["path"])

            print("----------------------------------")
            print(f"project: {name}\ntargets:")
            for target in project.targets.values():
                print(f"{target.target}: name={target.name} type={target.type}")
            print("----------------------------------")
        for name in rem: self.removeProject(name)

    def storeProject(self, name: str) -> None:
        path = os.path.join(self.PROJECT_DIR, f"{name}.json")
        try:
            with open(path, "w") as f:
                json.dump(self.project.data, f, indent=4)
        except IOError:
            self.log("project store failed", "error")
            sys.exit(1)

        self.projects[name] = path
        try:
            with open(self.PROJECTS, "w") as f:
                json.dump(self.projects, f, indent=4)
        except IOError:
            self.log("projects store failed", "error")
            sys.exit(1)
        self.log(f"stored project: {name}", "info")

    def removeProject(self, name: str) -> None:
        if name not in self.projects:
            self.log(f"project not found: {name}", "error")
            return

        path = self.projects[name]
        if not os.path.exists(path):
            self.log(f"project not found: {name} @ {path}", "error")
            sys.exit(1)

        del self.projects[name]
        try:
            with open(self.PROJECTS, "w") as f:
                json.dump(self.projects, f, indent=4)
        except IOError:
            self.log("projects remove failed", "error")
            sys.exit(1)
        os.remove(path)
        self.log(f"removed project: {name}", "info")

    def renameProject(self, old: str, new: str) -> None:
        if old not in self.projects:
            self.log(f"project not found: {old}", "error")
            return

        oldPath = self.projects[old]
        newPath = os.path.join(self.PROJECT_DIR, f"{new}.json")
        if not os.path.exists(oldPath):
            self.log(f"old project not found: {old} @ {oldPath}", "error")
            sys.exit(1)

        del self.projects[old]
        self.projects[new] = newPath
        try:
            with open(oldPath, "r") as f:
                oldData = json.load(f)

            with open(newPath, "w") as f:
                json.dump(oldData, f, indent=4)
        except IOError:
            self.log("project rename failed", "error")
            sys.exit(1)        

        os.remove(oldPath)
        try:
            with open(self.PROJECTS, "w") as f:
                json.dump(self.projects, f, indent=4)
        except IOError:
            self.log("projects rename failed", "error")
            sys.exit(1)
        self.log(f"renamed project: {old} -> {new}", "info")


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
        if not os.path.exists(self.REMOTE_DIR):
            os.makedirs(self.REMOTE_DIR, exist_ok=True)
        if not os.path.exists(self.PROJECT_DIR):
            os.makedirs(self.PROJECT_DIR, exist_ok=True)
        if not os.path.exists(self.PROJECTS):
            with open(self.PROJECTS, "w") as f:
                json.dump({}, f, indent=4)
        with open(self.PROJECTS, "r") as f:
            self.projects = json.load(f)

        self.newArg("target", "t", default="main")
        self.newArg("remove", "rem")
        self.newArg("rename", "ren", nargs=2)
        self.newArg("run", "r", empty=True)
        self.newArg("dump", "d", empty=True)
        self.newArg("store", "s", empty=True)
        self.newArg("list", "ls", empty=True)
        self.newArg("multi", "m", empty=True)
        self.newArg("clean", "c", empty=True)
        self.newArg("version", "v", empty=True)
        self.newArg("verbose", "vb", empty=True)
        args = self.parser.parse_args()

        if args.version:
            self.log(f"version: {self.VERSION}", "info")
            return

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
        if args.target not in self.r3make:
            self.log(f"target not found: {args.target}", "error")
            return
        
        self.project = R3Project(self.r3make, os.getcwd())
        if args.store:
            name = self.r3make.get("project", None)
            if name is None:
                self.log("project name required for storage.", "error")
                return
            self.storeProject(name)
            return

        if args.list:
            self.listProjects()
            return
        if args.remove:
            self.removeProject(args.remove)
            return
        if args.rename:
            self.renameProject(args.rename[0], args.rename[1])
            return

        self.root = self.r3make.get("root", '.')
        if args.target == "all":
            for t in self.r3make.get("all", []):
                target = R3BuildTarget(t, self.r3make[t])
                self.build(R3Reference(self.project, target))
        else: self.build(R3Reference(self.project, R3BuildTarget(args.target, self.r3make[args.target])))


def main() -> None:
    r3make = R3Make()
    r3make.main()

if __name__ == "__main__":
    main()