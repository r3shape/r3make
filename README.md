# r3make
![PyPi Package version](https://img.shields.io/pypi/v/r3make?style=for-the-badge&logo=pypi&logoColor=white&label=r3make&labelColor=black&color=white&link=https%3A%2F%2Fpypi.org%2Fproject%2Fr3make%2F2025.0.2%2F
)

r3make is a lightweight and straightforward command-line build tool for C projects. It simplifies the compilation process without the complexity of tools like CMake, making it perfect for small to medium-sized projects with minimal dependencies.

<br>

## Features

- **Simple JSON Configuration**: Define project settings in a JSON-based `.r3make` file.
- **Compiler Support**: Currently supports MinGW GCC, with plans to support Emscripten, Clang, MSVC, and more.
- **Automatic Source Management**: Collects `.c` files from specified directories for compilation.
- **Flexible Target Output**: Build executables (`.exe`), shared libraries (`.dll`/`.so`/`.dylib`), and soon static libraries (`.a`/`.lib`).
- **Cross-Platform Design**: While currently built and maintained on Windows, future updates aim to support Linux and MacOS.

<br>

## Installation

Install via [PyPI](https://pypi.org/project/r3make):

```bash
pip install r3make
```

<br>

## Getting Started

### Step 1. Create a `.r3make` Configuration File

The `.r3make` file now uses JSON format to specify project settings. Here's an example configuration:

```json
{
    "r3make": {
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

- **(Optional) `r3make`**: Dictionary of pre and post r3make commands for this build.
- **`c-instance`**: Compiler to use (currently supported: GCC, CLANG, EMCC).
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

Run the following command, specifying your `.r3make` configuration file:

```bash
r3make myproject.r3make
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
myproject.r3make
```

A `.r3make` configuration would look like this:
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

#### [ NOTE: r3make will create and store object files at `config[out-dir]\\ofiles`. This directory can be safely removed after a build has completed wither manually or with the `nofiles` post-build command. ]

<br>


## Why r3make?

While tools like CMake are powerful, they can be overly complex for straightforward tasks. r3make focuses on simplicity and ease of use, letting you focus on writing code rather than managing build configurations.

<br>

## r3make's Wishlist

1. **Improved Error Handling**:
   - Provide more descriptive errors when builds fail.
   - Catch common misconfigurations in the `.r3make` file.

2. **Incremental Builds**:
   - Implement a mechanism to skip recompilation of unchanged files.

3. **Verbose Mode**:
   - Add a CLI flag for detailed logging of compilation steps.

4. **Parallel Builds**:
   - Utilize multiple CPU cores to speed up compilation.

<br>

## Contributing

Contributions are welcome! If you encounter issues or have feature suggestions, feel free to open an issue or submit a pull request on GitHub.

<br>

## License

r3make is licensed under the MIT License. See `LICENSE` for more information.
