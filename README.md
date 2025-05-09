# r3make

![PyPi Package version](https://img.shields.io/pypi/v/r3make?style=for-the-badge\&logo=pypi\&logoColor=white\&label=r3make\&labelColor=black\&color=white)

**r3make** is a minimal, fast, and readable JSON-based build tool for C projects. It handles basic compilation and linking tasks with zero setup complexity, making it ideal for small-to-medium codebases that don't need the overhead of tools like CMake.

---

## Features

* **Straightforward JSON Config** – All build logic lives in a clean, intuitive JSON file.
* **Multi-Target Support** – Define any number of build targets in a single file.
* **Flexible Output** – Supports building executables, shared libraries, and static libraries.
* **Cross-Compiler** – Works with GCC, Clang, Emscripten, and MSVC.
* **Cross-Platform (Work in Progress)** – Windows is fully supported, with Linux and macOS planned.
* **Optional `--run` Flag** – Automatically run the built executable target after compilation.

---

## Why r3make?

Makefile and CMake are powerful but overly complex for many use cases. `r3make` gives you:

* A single clean JSON file.
* No scripts or Makefile DSL.
* Easier cross-compilation setup.
* Simpler onboarding for contributors.

---

## Getting Started

### 1. Create a `r3make.json` file in your project root

A minimal example utilizing all config fields:

```json
{
    "MyApp": {
        "defines": ["MYAPP_BUILD"],
        "flags": ["-Wall", "-Werror", "-std=c99"],

        "includes": ["include"],
        "sources": ["src/*.c"],
        
        "libraries": {"gdi32": null, "SSDK": null},
        "gitdeps": ["r3shape/SSDK"],

        "name": "App",
        "type": "exe",
        "dest": "bin"
    }
}
```

## Building a Project

Run this from the directory containing `r3make.json`:

```bash
r3make --target MyApp
```

To run an executable immediately after building:

```bash
r3make --target MyApp --run
```
| <b>NOTE:  
| If the `name` field is not present in a r3make target, the target name is used.  
| r3make configuration files may have a target named "main", this is the default target when calling `r3make` with no `--target` flag. </b>

---

## Fetching Remote Libraries
Consider the following program:

```c
#include <include/SSDK/SSDK.h>

int main() {
    ssdkInitLog();
    saneLog->log(SANE_LOG_DUMP, "Hello, World!");
    ssdkExitLog();
    return 0;
}
```

The above code is using the [SSDK](https://github.com/r3shape/SSDK) library, but we have not installed [SSDK](https://github.com/r3shape/SSDK) ourselves.
We can let `r3make` take care of installation, updates, and linking with [SSDK](https://github.com/r3shape/SSDK) via our configuration:

```json
{
    "main": {
        "sources": ["main.c"],
        
        "libraries": {"SSDK": null},
        "gitdeps": ["r3shape/SSDK"],
        
        "name": "app",
        "type": "exe",
        "dest": "build"
    }
}
```

With the above configuration, we can use the following command to build, link, and run `app.exe`:

```bash
r3make -r
```

You should see a log similar to `[INFO] Added library 'SSDK' from r3shape/SSDK` in the stream of output from `r3make`, verifying the successful clone/update, and build of the remote dep.

| <b>NOTE:</b>  
| A [WARNING] log might appear when utilizing the `gitdeps` field, as an <b>elevated shell</b> is required for OS-default path manipulation, which is where remote deps are installed to.
| 

---

## Target Configuration Fields

| Field       | Required | Description                                        |
| ----------- | -------- | -------------------------------------------------- |
| `sources`   | Yes      | List of glob patterns or file paths to `.c` files. |
| `type`      | Yes      | `exe`, `dll`, or `lib` (shared/static libraries).  |
| `dest`      | Yes      | Output directory for built files.                  |
| `name`      | No       | The name of the output artifact.                   |
| `flags`     | No       | Additional compiler flags.                         |
| `defines`   | No       | List of preprocessor defines.                      |
| `gitdeps`   | No       | List of remote linked libraries.                   |
| `includes`  | No       | List of include directories.                       |
| `libraries` | No       | Linked libraries, optionally with paths.           |

---

## CLI Flags
| Short Flag | Long Flag     | Description                                                                 |
| ---------- | ------------- | --------------------------------------------------------------------------- |
| `-t`       | `--target`    | Name of the target to build (e.g., `-t MyApp`). Required unless defaulting. |
| `-v`       | `--verbose`   | Enables verbose output (shows full commands and file list).                 |
| `-f`       | `--file`      | Path to the `r3make.json` config file (defaults to `r3make.json` in current dir).   |
| `-nf`      | `--nofiles`   | Disables file discovery; skips glob expansion (useful for debugging).       |
| `-be`      | `--buildeach` | Forces compilation of all sources individually, even if a library.          |
| `-r`       | `--run`       | Runs the target after a successful build (only works for `exe` targets).    |

---

## Installation

Install via pip:

```bash
pip install r3make
```

---

## Roadmap

* [ ] Incremental builds (skip unchanged files).
* [ ] Parallel compilation.
* [ ] Better error messages and diagnostics.
* [ ] Linux/macOS support.
* [✔️] Remote dependency fetching (`gitdeps` config field).

---

## Contributing

Issues and pull requests are welcome! If you find a bug, want to suggest a feature, or improve documentation, visit [github.com/r3shape/r3make](https://github.com/r3shape/r3make).

---

## License

MIT License. See [LICENSE](LICENSE).
