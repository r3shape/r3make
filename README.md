# r3make
**r3make** is a minimal, JSON-based build tool for C projects.  
Build targets, compiler options, dependencies, include paths, output locations, and project relationships are defined in a single `r3make.json` file.

## Table of Contents

- [r3make](#r3make)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Command Line Options](#command-line-options)
  - [Configuration](#configuration)
    - [Project Fields](#project-fields)
  - [Target Configuration](#target-configuration)
    - [Target Types](#target-types)
  - [References](#references)
    - [Requirements](#requirements)
    - [Dependencies](#dependencies)
  - [Project Registry](#project-registry)
  - [Local Dependencies](#local-dependencies)
  - [GitHub Dependencies](#github-dependencies)
  - [Compiler Flags](#compiler-flags)
  - [Includes and Defines](#includes-and-defines)
  - [Multi Mode](#multi-mode)
  - [Clean Mode](#clean-mode)
  - [Run Mode](#run-mode)
  - [Compile Commands](#compile-commands)
  - [Compiler Detection](#compiler-detection)
  - [Example Project](#example-project)
  - [Design](#design)
  - [Installation](#installation)
  - [Roadmap](#roadmap)
  - [Contributing](#contributing)
  - [License](#license)


## Features

* **Simple JSON configuration** — Define a project using one configuration file.
* **Multiple targets** — Build executables, shared libraries, and static libraries.
* **Target references** — Aggregate configuration from intra-project and inter-project targets using `@target` and `@project::target`.
* **Target requirements** — Build required targets automatically.
* **Local dependencies** — Link against libraries using explicit paths.
* **Remote dependencies** — Clone and build GitHub repositories containing `r3make.json`.
* **Recursive dependencies** — Dependencies can have their own dependencies.
* **Project storage** — Register, list, remove, and rename projects for cross-project references.
* **Dependency caching** — Reuse cloned GitHub repositories and their build artifacts.
* **GCC, Clang, and MSVC** — Automatically detect an available compiler.

## Command Line Options

| Short  | Long        | Description                                              |
| ------ | ----------- | -------------------------------------------------------- |
| `-t`   | `--target`  | Target to build. Defaults to `main`.                     |
| `-s`   | `--store`   | Store the current project for cross-project references.  |
| `-ls`  | `--list`    | List stored projects and their targets.                  |
| `-rem` | `--remove`  | Remove a project from the project registry.              |
| `-ren` | `--rename`  | Rename a stored project. Requires the old and new names. |
| `-v`   | `--version` | Output the installed r3make version.                     |
| `-vb`  | `--verbose` | Enable verbose build output.                             |
| `-m`   | `--multi`   | Build each source as a separate artifact.                |
| `-c`   | `--clean`   | Remove object files after building.                      |
| `-r`   | `--run`     | Run the resulting executable.                            |
| `-d`   | `--dump`    | Generate/update `compile_commands.json`.                 |

For example:

```bash
r3make -t test -vb
```

## Configuration

A minimal `r3make.json` looks like:

```json
{
    "project": "project1",
    "main": {
        "type": "exe",
        "name": "project1",
        "dest": "bin",
        "sources": ["src/*.c"]
    }
}
```

The `main` target is used when no target is specified.

### Project Fields

| Field     | Description                                                 |
| --------- | ----------------------------------------------------------- |
| `project` | Project name used by `-s` and cross-project references.     |
| `root`    | Root directory for project-relative paths. Defaults to `.`. |
| `all`     | Targets built when `-t all` is used.                        |

Example:

```json
{
    "project": "project1",
    "root": ".",
    "all": ["main", "test"]
}
```

Run all configured targets with:

```bash
r3make -t all
```

## Target Configuration

Targets are defined as objects in `r3make.json`.

| Field      | Required | Description                                 |
| ---------- | -------- | ------------------------------------------- |
| `type`     | Yes      | Target type.                                |
| `name`     | No       | Artifact name. Defaults to the target name. |
| `dest`     | Yes      | Output directory.                           |
| `sources`  | Yes      | Source files or glob patterns.              |
| `includes` | No       | Include directories.                        |
| `ccflags`  | No       | Compiler flags.                             |
| `ldflags`  | No       | Linker flags.                               |
| `defines`  | No       | Preprocessor definitions.                   |
| `requires` | No       | Targets that must be built first.           |
| `deps`     | No       | Libraries or other link dependencies.       |

### Target Types

| Type                             | Artifact       |
| -------------------------------- | -------------- |
| `exe`, `executable`              | Executable     |
| `so`, `dll`, `shared`, `dynamic` | Shared library |
| `lib`, `static`                  | Static library |

Artifact extensions are platform-dependent. Windows uses `.exe`, `.dll`, and `.lib`; other platforms use `.so`, `.a`, and no executable extension.

## References

r3make uses `@` to reference another target and aggregate its configuration data into the referencing target.

There are two forms:

```text
@target
@project::target
```

`@target` references a target in the current project.

`@project::target` references a target in another project registered with r3make.

References can be used by fields that accept target configuration, such as `ccflags`, `ldflags`, `includes`, `dest`, and `deps`.

For example:

```json
{
    "main": {
        "type": "dll",
        "dest": "bin",
        "ccflags": ["std=c11"],
        "includes": ["include"]
    },
    "test": {
        "type": "exe",
        "dest": "@main",
        "ccflags": ["@main", "Wall"],
        "includes": ["@main"],
        "sources": ["test/*.c"]
    }
}
```

When a field contains `@main`, r3make recursively resolves that target's corresponding field and adds its values to the referencing target.

This allows target configuration to be shared without copying it.

### Requirements

`requires` makes a referenced target a dependency of the current target and builds it before the current target.

```json
{
    "test": {
        "type": "exe",
        "requires": ["@main"],
        "sources": ["test/*.c"]
    }
}
```

The required target's artifact and include directories become available to the referencing target. Its include directories are passed with `-I`, and its artifact is linked using `-L` and `-l`.

The same mechanism works across projects:

```json
"requires": ["@project1::main"]
```

### Dependencies

A target reference can also be placed directly in `deps`:

```json
{
    "test": {
        "type": "exe",
        "deps": ["@project1::main"]
    }
}
```

r3make builds the referenced target if its artifact does not already exist, then treats it as a link dependency of the referencing target.

Its artifact is added through `-L` and `-l`, and dependencies of the referenced target are resolved recursively.

Use `@` by itself when you want to reuse target configuration.

Use `requires` when the referenced target *must be built* and consumed by the current target.

Use a target reference in `deps` when the referenced target *should be built if necessary* and consumed by the current target.

## Project Registry

Projects must be stored before they can be referenced from another project.

Store the current project:

```bash
r3make -s
```

List stored projects:

```bash
r3make -ls
```

Remove a stored project:

```bash
r3make -rem project1
```

Rename a stored project:

```bash
r3make -ren project1 project2
```

`--list` displays each registered project and its available targets. Missing or invalid project entries are automatically removed from the registry.

The registry is stored at:

```text
~/r3make/projects.json
```

Stored project metadata is kept under:

```text
~/r3make/projects/
```

The project's `project` field determines its registry name:

```json
{
    "project": "project1"
}
```

Cross-project references use this name:

```text
@project1::main
```

The referenced project does not need to have been built beforehand. If its artifact does not exist, r3make builds it automatically.

## Local Dependencies

Local libraries use:

```text
path/to::library
```

For example:

```json
"deps": [
    "extern/bin::library"
]
```

This produces the equivalent of:

```text
-L<project>/extern/bin
-llibrary
```

The special `~` path can be used for libraries already available to the system linker:

```json
"deps": [
    "~::library"
]
```

## GitHub Dependencies

GitHub repositories containing an `r3make.json` can be specified with:

```text
github::user/repository
```

For example:

```json
"deps": [
    "github::user/project"
]
```

r3make:

1. Clones the repository if it is not already cached.
2. Reads its `r3make.json`.
3. Builds its `main` target if the artifact does not exist.
4. Adds the resulting library to the current target.

Repositories are cached under:

```text
~/r3make/deps/github/
```

GitHub dependencies can contain their own dependencies, allowing dependency trees to be resolved recursively.

## Compiler Flags

Compiler flags are specified with `ccflags`:

```json
"ccflags": [
    "std=c11",
    "O2",
    "Wall"
]
```

r3make automatically adds `-` where necessary:

```text
-std=c11 -O2 -Wall
```

Flags beginning with `-` are preserved.

Linker-specific options use `ldflags`:

```json
"ldflags": [
    "pthread"
]
```

## Includes and Defines

Include directories:

```json
"includes": [
    "include",
    "extern/include"
]
```

become:

```text
-Iinclude
-Iextern/include
```

Preprocessor definitions:

```json
"defines": [
    "DEBUG",
    "PROJECT_BUILD"
]
```

become:

```text
-DDEBUG -DPROJECT_BUILD
```

## Multi Mode

Normally all source files are compiled and then linked into one artifact.

With:

```bash
r3make -m
```

each source is compiled and linked separately, with the output name derived from the source filename.

## Clean Mode

`--clean` removes intermediate object files after a successful build:

```bash
r3make -c
```

The final artifact is retained.

## Run Mode

`--run` executes the resulting executable:

```bash
r3make -r
```

Only executable targets are run.

## Compile Commands

`--dump` generates `compile_commands.json`:

```bash
r3make -d
```

Each compilation command records the command, working directory, and source file.

## Compiler Detection

r3make searches for compilers in this order:

```text
gcc
clang
cl
```

The first available compiler is used.

## Example Project

A typical project can be structured as:

```text
project1/

├── r3make.json
├── include/
├── src/
└── bin/
```

with:

```json
{
    "project": "project1",
    "main": {
        "type": "exe",
        "name": "project1",
        "dest": "bin",
        "ccflags": ["std=c99", "Wall", "Werror"],
        "includes": ["include"],
        "sources": ["src/*.c"]
    }
}
```

Running:

```bash
r3make -c
```

builds the `main` target and cleans up any generated `.o` object files producing `bin/project1.exe`.

## Design

r3make keeps build descriptions close to the projects they belong to.

Targets can expose their configuration to other targets through references:

```text
@target
```

references a target in the current project.

```text
@project::target
```

references a target in another registered project.

This allows projects to share build configuration and dependencies without copying their build definitions.

## Installation

Prebuilt Windows releases are available from the releases page.

Place the executable somewhere on your `PATH` and run:

```bash
r3make -v
```

## Roadmap

* [ ] Build hashing.
* [ ] Improved diagnostics and error reporting.
* [ ] Dependency/version management.
* [ ] Incremental builds.
* [ ] Parallel compilation.

## Contributing

Issues, feature requests, and pull requests are welcome.

## License

r3make is released under the MIT License.

See [LICENSE](LICENSE) for the full license text.
