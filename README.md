# CBuild

CBuild is a lightweight and straightforward command-line build tool for C projects. It simplifies the compilation process without the complexity of tools like CMake, making it perfect for small to medium-sized projects with minimal dependencies.

<br>

## Features

- **Simple JSON Configuration**: Define project settings in a JSON-based `.cbuild` file.
- **Compiler Support**: Currently supports MinGW GCC, with plans to support Emscripten, Clang, MSVC, and more.
- **Automatic Source Management**: Collects `.c` files from specified directories for compilation.
- **Flexible Target Output**: Build executables (`.exe`), shared libraries (`.dll`/`.so`), and static libraries (`.a`).
- **Cross-Platform Design**: While currently targeting Windows, future updates aim to support Linux and macOS.

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
    "compiler": "MinGW",
    "project": "MyProject",
    "include_dirs": ["include"],
    "source_files": [],
    "source_dirs": ["src"],
    "libraries": {
        "gdi32": null,
        "opengl32": null
    },
    "flags": [],
    "defines": [],
    "output": "exe",
    "output_dir": "build"
}
```

- **`compiler`**: Compiler to use (e.g., MinGW, Clang).
- **`project`**: Name of the output file (without extension).
- **`include_dirs`**: List of directories to search for header files.
- **(Optional) `source_files`**: List of paths to source files.
- **`source_dirs`**: Directories containing source files.
- **`libraries`**: Key-value pairs of libraries to link. Value is optional for default system paths.
- **(Optional) `flags`**: List of compiler flags to be used during this build.
- **(Optional) `defines`**: List of project directives to be defined by the pre-processor.
- **`output`**: Type of output file (`exe`, `dll`, `a`, etc.).
- **`output_dir`**: Directory for generated output.

<br>

### Step 2. Build Your Project

Run the following command, specifying your `.cbuild` configuration file:

```bash
cbuild myproject.cbuild
```

This will compile and link your project, placing the output in the specified `output_dir`.

<br>

## Example Usage

Given the following directory structure:

```
MyProject/
├── src/
│   ├── main.c
│   ├── utils.c
├── include/
│   ├── utils.h
├── myproject.cbuild
```

A `.cbuild` configuration like the one in **Step 1** will:

1. Compile `main.c` and `utils.c` into object files.
2. Link them into an executable called `MyProject.exe` in the `build` directory.

#### [ NOTE: CBuild will create and store object files at `config[output_dir]\\ofiles`. This directory can be safely removed after a build has completed. ]

<br>


## Why CBuild?

While tools like CMake are powerful, they can be overly complex for straightforward tasks. CBuild focuses on simplicity and ease of use, letting you focus on writing code rather than managing build configurations.

<br>

## CBUILD's Wishlist

1. **Add Compiler Support**:
   - Extend support for Emscripten, Clang, MSVC, and other compilers.
   - Auto-detect the default system compiler.

2. **Cross-Platform Compatibility**:
   - Test and adapt for Linux and macOS environments.
   - Replace calls to `os.system` with `subprocess` for better portability.

3. **Custom Build Scripts**:
   - Allow users to toggle pre-build or post-build routines.

4. **Improved Error Handling**:
   - Provide more descriptive errors when commands fail.
   - Catch common misconfigurations in the `.cbuild` file.

5. **Incremental Builds**:
   - Implement a mechanism to skip recompilation of unchanged files.

6. **Verbose Mode**:
   - Add a CLI flag for detailed logging of compilation steps.

7. **Parallel Builds**:
   - Utilize multiple CPU cores to speed up compilation.

<br>

## Contributing

Contributions are welcome! If you encounter issues or have feature suggestions, feel free to open an issue or submit a pull request on GitHub.

<br>

## License

CBuild is licensed under the MIT License. See `LICENSE` for more information.
