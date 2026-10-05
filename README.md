# r3make

**r3make** is a minimal, JSON-based build tool for C projects.

It is designed for projects that want a simple build system without the configuration overhead of tools such as CMake. Build targets, compiler options, dependencies, include paths, and output locations are described in a single `r3make.json` file.

## Features

* **Simple JSON configuration** — Define your entire build in one readable JSON file.
* **Multiple targets** — Build executables, shared libraries, and static libraries from the same configuration.
* **Target dependencies** — Targets can require other targets in the same project.
* **GitHub dependencies** — Dependencies can be pulled directly from GitHub and built using their own `r3make.json`.
* **Recursive dependencies** — GitHub dependencies can have their own dependencies.
* **Dependency caching** — Cloned repositories and built artifacts are reused instead of being downloaded and rebuilt unnecessarily.
* **GCC, Clang, and MSVC** — r3make automatically detects an available compiler.
* **Cross-platform design** — Windows is currently supported, with additional platform support planned.
* **Small and readable** — No build-language DSL or generated project files are required.


## Command Line Options

| Short | Long        | Description                          |
| ----- | ----------- | ------------------------------------ |
| `-t`  | `--target`  | Target to build. Defaults to `main`. |
| `-v`  | `--version` | Output the installed r3make version. |
| `-vb` | `--verbose` | Enable verbose build output.         |
| `-m`  | `--multi`   | Build each source as a separate artifact. |
| `-c`  | `--clean`   | Clean mode.                          |
| `-r`  | `--run`     | Run mode.                            |
| `-d`  | `--dump`    | Dump mode.                           |

For example:

```bash
r3make -t app
```

or:

```bash
r3make --target app --verbose
```

## Why r3make?

C projects do not always need a large build system.

For smaller projects, a build configuration can often be expressed as a few paths, compiler options, and dependencies. r3make keeps those things explicit without requiring a separate build language.

A typical project consists of:

```text
include/
src/
bin/
```

Thus a monolithic, hyper configurable build system might be overkill.


## Getting Started

Create a `r3make.json` file in the root of your project:

```json
{
    "main": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "ccflags": ["std=c99", "Wall", "Werror"],
        "defines": ["APP_BUILD"],
        "includes": ["include"],
        "sources": ["src/*.c"]
    }
}
```

Then run:

```bash
r3make
```

The target named `main` is the default target when no target is specified.

You can explicitly select a target with:

```bash
r3make -t main
```

## Project Configuration

A `r3make.json` can define top-level fields that apply to the project as a whole:

| Field  | Required | Description                                          |
| ------ | -------- | ---------------------------------------------------- |
| `root` | No       | Root directory of the project. Defaults to `.`.      |
| `all`  | No       | List of targets to build when `-t all` is specified. |

For example:

```json
{
    "root": ".",
    "all": ["main", "test"],

    "main": {
        "type": "dll",
        "name": "ecx",
        "dest": "bin",
        "sources": ["src/ecx.c"]
    },

    "test": {
        "type": "exe",
        "name": "test",
        "dest": "bin",
        "sources": ["src/test.c"],
    }
}
```
| Note: targets listed in `all` should be 'final' targets, meaning if they provide a `requires` field with targets that are also listed in `all`, those targets will be built twice.

`root` determines the directory from which project paths are resolved. This is particularly useful for projects whose build configuration is stored separately from their source tree.

`all` defines the project's final targets. Running:

```bash
r3make -t all
```

builds each target listed in `all`, with any targets required by them being built automatically.

### Target Types

r3make supports three primary target types:

| Type  | Output                                                       |
| ----- | ------------------------------------------------------------ |
| `exe`, `executable` | Executable                                                   |
| `so`, `shared` | Shared library (`.dll` on Windows, `.so` on other platforms) |
| `lib`, `static` | Static library (`.lib` on Windows, `.a` on other platforms)  |

The target's `name` determines the name of the generated artifact.

If `name` is omitted, the target name will be used as the artifact name.

## Target Configuration

A target can contain the following fields:

| Field      | Required | Description                                                       |
| ---------- | -------- | ----------------------------------------------------------------- |
| `type`     | Yes      | Target type: `exe`, `dll`, or `lib`.                              |
| `dest`     | Yes      | Directory where the target is built.                              |
| `name`     | No       | Name of the generated artifact.                                   |
| `sources`  | Yes      | Source files or glob patterns.                                    |
| `includes` | No       | Include directories.                                              |
| `ccflags`  | No       | Compiler flags.                                                   |
| `ldflags`  | No       | Linker flags.                                                     |
| `defines`  | No       | Preprocessor definitions.                                         |
| `requires` | No       | Other targets in the same `r3make.json` that must be built first. |
| `deps`     | No       | External libraries or GitHub dependencies.                        |

For example:

```json
{
    "main": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "ccflags": ["std=c99", "Wall", "Werror"],
        "defines": ["APP_BUILD"],
        "includes": ["include"],
        "sources": ["src/*.c"],
        "deps": ["extern/bin:foo"]
    }
}
```

## Multiple Targets

A single `r3make.json` can define any number of targets:

```json
{
    "library": {
        "type": "dll",
        "name": "mylib",
        "dest": "bin",
        "ccflags": ["std=c99", "O2"],
        "includes": ["include"],
        "sources": ["src/*.c"]
    },

    "app": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "includes": ["include"],
        "sources": ["app/*.c"],
        "requires": ["library"]
    }
}
```

Building `app` automatically builds `library` first.

```bash
r3make -t app
```

The resulting build relationship is:

```text
app
└── library
```

This allows projects to organize their build into independent libraries and executables without requiring separate build configurations.

## Reusing Target Configuration

When a project contains multiple targets, r3make allows target fields to reference another target using the `@target` syntax.

This is useful when multiple targets share compiler flags, include directories, output directories, or dependencies.

For example:

```json
{
    "main": {
        "type": "so",
        "name": "ecx",
        "dest": "bin",
        "sources": ["src/ecx.c"],
        "ccflags": ["std=c99", "O2"],
        "deps": ["github:zafflins/zafflib"],
        "includes": ["include", "extern/include"]
    },

    "test": {
        "type": "exe",
        "name": "test",
        "dest": "@main",
        "deps": ["@main"],
        "requires": ["main"],
        "ccflags": ["@main"],
        "includes": ["@main"],
        "sources": ["src/test.c"],
    }
}
```

Here, `test` uses the configuration from `main` where appropriate. Notice how the `test` target does not list the `ecx` artifact in its deps, as r3make will automatically add any targets listed in the `requires` field as dependencies. The `@` syntax therefore acts as a reference to another target's corresponding field.

### Fields That Can Be Reused

The following fields support `@target` references:

* `deps`
* `dest`
* `ccflags`
* `ldflags`
* `includes`

For list fields, referencing another target appends that target's values to the current target's values rather than replacing them.

For example:

```json
{
    "main": {
        "ccflags": ["std=c99", "O2"]
    },

    "test": {
        "ccflags": ["@main"]
    }
}
```

results in `test` receiving the compiler flags defined by `main`.

A target can also add its own values:

```json
{
    "test": {
        "ccflags": ["@main", "Wall", "Werror"]
    }
}
```

which combines the referenced flags with the test target's additional flags.

### Fields That Must Be Defined Per Target

`type`, `name`, `sources`, and `requires` are target-specific and must be defined independently.

This means a test executable can reuse the build configuration of a library without accidentally becoming the same target:

```json
{
    "main": {
        "type": "dll",
        "name": "ecx",
        "sources": ["src/ecx.c"]
    },

    "test": {
        "type": "exe",
        "name": "test",
        "sources": ["src/test.c"],
        "dest": "@main"
    }
}
```

The result is two distinct targets:

```text
main -> bin/ecx.dll
test -> bin/test.exe
```

while both targets can share the same output directory and other configuration through `@main`.

This makes it possible to keep related targets in a single `r3make.json` without duplicating configuration.

## Dependencies

r3make supports local libraries and GitHub dependencies.

### Local Libraries

A dependency can specify a library directory and library name using:

```text
path/to:library
```

or using a tilde `~` as the path for known/system libraries:
```text
~:opengl32
```

For example:

```json
{
    "main": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "sources": ["src/*.c"],
        "deps": ["extern/bin:foo"]
    }
}
```

This causes r3make to add the appropriate `-L` and `-l` options when linking.

### GitHub Dependencies

GitHub dependencies use:

```text
github:user/repository
```

For example:

```json
{
    "main": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "sources": ["src/*.c"],
        "deps": [
            "github:zafflins/zafflib"
        ]
    }
}
```

The dependency must contain a `r3make.json` at the root of its repository.

When r3make encounters a GitHub dependency, it:

1. Clones the repository into r3make's dependency cache if it has not already been cloned.
2. Reads the dependency's `r3make.json`.
3. Builds the dependency if its artifact does not already exist.
4. Resolves the dependency's include directory and library output.
5. Links the dependency into the current target.

Dependencies are stored in the user's r3make dependency directory:

```text
~/r3make/deps/github/user
```

This means removing a dependency's build output will cause it to be rebuilt, while removing the repository itself will cause it to be cloned again.

### Recursive Dependencies

GitHub dependencies are themselves r3make projects, so dependencies can depend on other dependencies.

For example:

```text
application
└── ecx
    └── zafflib
```

If `application` declares:

```json
"deps": [
    "github:zafflins/ecx"
]
```

and `ecx` declares:

```json
"deps": [
    "github:zafflins/zafflib"
]
```

r3make automatically resolves the entire dependency chain.

The application does not need to know that `ecx` depends on `zafflib`.

## Compiler Flags

Compiler options are specified using `ccflags`:

```json
"ccflags": [
    "std=c99",
    "O2",
    "Wall",
    "Werror"
]
```

r3make automatically adds the `-` prefix when necessary, so the above becomes:

```text
-std=c99 -O2 -Wall -Werror
```

Flags that already begin with `-` are preserved:

```json
"ccflags": [
    "-std=c99",
    "-O2"
]
```

Linker-specific options can be specified separately with `ldflags`:

```json
"ldflags": [
    "-pthread"
]
```

## Includes and Defines

Include directories are specified with `includes`:

```json
"includes": [
    "include",
    "extern/include"
]
```

Preprocessor definitions are specified with `defines`:

```json
"defines": [
    "MYLIB_BUILD",
    "DEBUG"
]
```

r3make converts these into the appropriate compiler arguments.

## Multi Mode

By default, all source files in a target are compiled into one artifact:

```text
src/test.c
src/test2.c
      ↓
test.o
test2.o
      ↓
test.exe
```

With --multi, each source file is compiled and linked independently. The output name is derived from the source filename:
```bash
r3make --multi
```

## Installation

Prebuilt Windows releases are available from the releases page.  
The executable can be placed somewhere on your `PATH` and invoked directly:

```bash
r3make
```

## Example Project
A simple project might look like:

```text
myproject/
├── r3make.json
├── include/
│   └── app.h
├── src/
│   ├── app.c
│   └── main.c
└── bin/
```

with:

```json
{
    "main": {
        "type": "exe",
        "name": "app",
        "dest": "bin",
        "ccflags": ["std=c99", "Wall", "Werror"],
        "includes": ["include"],
        "sources": ["src/*.c"]
    }
}
```

Running:

```bash
r3make
```

produces:

```text
myproject/
├── r3make.json
├── include/
├── src/
└── bin/
    ├── app.exe
    ├── app.o
```


## Roadmap

* [ ] Build hashing to detect when targets actually need rebuilding.
* [ ] Improved diagnostics and error reporting.
* [ ] Additional dependency/version management.
* [ ] Incremental builds based on source/build state.
* [ ] Parallel compilation.

## Contributing

Issues, feature requests, and pull requests are welcome.

## License

r3make is released under the MIT License.

See [LICENSE](LICENSE) for the full license text.
