from r3make.util import os, json

def clangdcmd(main_config, config_path) -> None:
    project_root = os.path.dirname(os.path.abspath(config_path))
    commands = []
    seen = set()

    includes = [f"-I{inc}" for inc in main_config.get("includes", [])]
    defines = [f"-D{d}" for d in main_config.get("defines", [])]
    flags = main_config.get("flags", [])
    sources = []
    for pattern in main_config.get("sources", []):
        sources.extend(__import__("glob").glob(pattern, recursive=True))

    for src in sources:
        abs_src = os.path.abspath(src)
        if abs_src in seen:
            continue
        seen.add(abs_src)

        cmd_parts = ["gcc"] + flags + defines + includes + ["-c", abs_src]
        commands.append({
            "directory": project_root,
            "command": " ".join(cmd_parts),
            "file": abs_src
        })

    with open(os.path.join(project_root, "compile_commands.json"), "w") as f:
        json.dump(commands, f, indent=2)

    return True

