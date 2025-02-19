# CBuild
![PyPi Package version](https://img.shields.io/pypi/v/cbuild?style=for-the-badge&logo=pypi&logoColor=white&label=Cbuild&labelColor=black&color=white&link=https%3A%2F%2Fpypi.org%2Fproject%2Fcbuild%2F2025.0.2%2F
)

CBuild is a lightweight and straightforward command-line build tool for C projects. It simplifies the compilation process without the complexity of tools like CMake, making it perfect for small to medium-sized projects with minimal dependencies.

<br>

## Features

- **Simple JSON Configuration**: Define project settings in a JSON-based `.cbuild` file.
- **Compiler Support**: Currently supports MinGW GCC, with plans to support Emscripten, Clang, MSVC, and more.
- **Automatic Source Management**: Collects `.c` files from specified directories for compilation.
- **Flexible Target Output**: Build executables (`.exe`), shared libraries (`.dll`/`.so`/`.dylib`), and soon static libraries (`.a`/`.lib`).
- **Cross-Platform Design**: While currently built and maintained on Windows, future updates aim to support Linux and MacOS.

<br>

## Installation

Install via [PyPI](https://pypi.org/project/cbuild):

```bash
pip install cbuild
```

<br>

## Getting Started

### Step 1. Create a `.cbuild` Configuration File

The `.cbuild` file now uses JSON format to specify project settings. Here's an example configuration:

```json
{
    "cbuild": {
        "pre-build": {},
        "post-build": {}
    },
    "c-instance": "GCC",
    "c-flags": [],
    "c-defines": [],
    "src-dirs": [],
    "inc-dirs": [],
    "lib-links": {},
    "out-dir": "bin",
    "out-type": "exe",
    "out-name": "program",
}
```

- **(Optional) `cbuild`**: Dictionary of pre and post cbuild commands for this build.
- **`c-instance`**: Compiler to use (e.g., MinGW GCC, Emscripten, Clang).
- **(Optional) `c-flags`**: List of compiler flags to be used during this build.
- **(Optional) `c-deines`**: List of project directives to be defined by the pre-processor.
- **`inc-dirs`**: List of directories to search for header files.
- **`src-dirs`**: Directories containing source files.
- **(Optional) `lib-links`**: Key-value pairs of libraries to link. Value is optional for default system paths.
- **`out-dir`**: Directory for generated output.
- **`out-type`**: Type of output file (`exe`, `dll`, `a`, etc.).
- **`out-name`**: Name of the output file (without extension).

<br>

### Step 2. Build Your Project

Run the following command, specifying your `.cbuild` configuration file:

```bash
cbuild myproject.cbuild
```

This will compile and link your project, placing the output in the specified `out-dir`.

<br>

## Example Usage

Given the following directory structure:

```
MyProject/
src/
   /main.c
   /utils.c
include/
       /utils.h
myproject.cbuild
```

A `.cbuild` configuration would look like this:
```json
{
    "c-instance": "GCC",
    "src-dirs": ["src"],
    "inc-dirs": ["include"],
    "out-dir": "bin",
    "out-type": "exe",
    "out-name": "MyProject",
}
```

This configuration will:
1. Compile `main.c` and `utils.c` into object files.
2. Link them into an executable called `MyProject.exe` in the `bin` directory.

#### [ NOTE: CBuild will create and store object files at `config[out-dir]\\ofiles`. This directory can be safely removed after a build has completed wither manually or with the `nofiles` post-build command. ]

<br>


## Why CBuild?

While tools like CMake are powerful, they can be overly complex for straightforward tasks. CBuild focuses on simplicity and ease of use, letting you focus on writing code rather than managing build configurations.

<br>

## CBUILD's Wishlist

1. **Add Compiler Support**:
   - Extend `BaseCompiler` with support for Emscripten, Clang, MSVC, and other compilers.
   - Auto-detect the default system compiler.

2. **Improved Error Handling**:
   - Provide more descriptive errors when builds fail.
   - Catch common misconfigurations in the `.cbuild` file.

3. **Incremental Builds**:
   - Implement a mechanism to skip recompilation of unchanged files.

4. **Verbose Mode**:
   - Add a CLI flag for detailed logging of compilation steps.

5. **Parallel Builds**:
   - Utilize multiple CPU cores to speed up compilation.

<br>

## Contributing

Contributions are welcome! If you encounter issues or have feature suggestions, feel free to open an issue or submit a pull request on GitHub.

<br>

## License

CBuild is licensed under the MIT License. See `LICENSE` for more information.
