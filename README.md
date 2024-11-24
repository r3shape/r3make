# CBuild
CBuild is a lightweight and straightforward command-line build tool for C projects, designed to simplify the compilation process without the bloat and complexity of CMake. It provides just enough functionality to compile and link C source code with ease, making it ideal for small to medium-sized projects.

<br>

## Features

- **Minimal Configuration**: Specify project details in a `.cbuild` configuration file.
- **Compiler Support**: Choose your compiler (currently supports MinGW GCC; others planned).
- **Automatic Dependency Handling**: Collects `.c` files from source directories and includes them in the build process.
- **Target Output**: Supports building executables (`.exe`), shared libraries (`.dll`), and static libraries (`.a`).
- **Cross-Platform Design**: Although developed with Windows in mind, future versions aim for broader compatibility.

<br>

## Installation

Install via [PyPI](https://pypi.org/project/cbuild):

```bash
pip install cbuild
```

<br>

## Getting Started

### Step 1. Create a `.cbuild` Configuration File

The `.cbuild` file defines your project settings. Here's an example:

```ini
[CBUILD]
compiler = gcc              # specify a compiler
defines = DEBUG             #  (comma-separated) pre-processing defines
source_dir = src            # target a directory for recursive search
sources = main.c, utils.c   #  (comma-separated) target specific source files
output_type = exe           # spcify the type of file returned
output_dir = build/         # specify the target output directory
libraries = m               #  (comma-separated) specify project ld flags
include_dirs = include      #  (comma-separated) specify paths to project include directories
library_dirs = lib          #  (comma-separated) specify paths to linked-libraries
project_name = MyProject    # specify the target output's name
```

### Step 2. Build Your Project

Run the following command, pointing to your `.cbuild` configuration file:

```bash
cbuild myproject.cbuild
```

This will compile and link your project, generating the output in the specified `output_dir`.

<br>

## Example Usage

Given a directory structure like this, the configuration outlined in `Step 1` will work just fine!:

```
MyProject/
├── src/
│   ├── main.c
│   ├── utils.c
├── include/
│   ├── utils.h
├── myproject.cbuild
```

Running `cbuild myproject.cbuild` will:

1. Compile `main.c` and `utils.c` into object files.
2. Link the object files into an executable called `MyProject.exe` in the `build/` directory.

<br>

## Why CBuild?

While tools like CMake are powerful, they can be overly complex for straightforward tasks. CBuild focuses on simplicity and ease of use, letting you focus on writing code rather than managing build configurations.

<br>

## CBUILD's Wishlist

1. **Add Compiler Support**:
   - Extend support for Clang, MSVC, and other compilers.
   - Auto-detect the default system compiler.

2. **Cross-Platform Compatibility**:
   - Test and adapt for Linux and macOS environments.
   - Replace calls to `os.system` with `subprocess` for better portability.

3. **Custom Build Scripts**:
   - Allow users to define pre-build or post-build commands.

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
