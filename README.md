# r3make
![PyPi Package version](https://img.shields.io/pypi/v/r3make?style=for-the-badge&logo=pypi&logoColor=white&label=r3make&labelColor=black&color=white&link=https%3A%2F%2Fpypi.org%2Fproject%2Fr3make%2F2025.0.2%2F
)

r3make is a straightforward command-line build tool for C projects. It simplifies the compilation process with less complexity and more readibility, making it perfect for small to medium-sized projects with minimal dependencies.

<br>

## Features

- **Simple JSON Configuration**: Define project settings in a JSON-based `.r3make` file.
- **Compiler Support**: Currently supports MinGW GCC, Emscripten, Clang, and MSVC.
- **Automatic Source Management**: Collects `.c` files from specified directories for compilation.
- **Flexible Target Output**: Build executables (`.exe`), shared libraries (`.dll`/`.so`/`.dylib`), and static libraries (`.a`/`.lib`).
- **Cross-Platform Design**: While currently built and maintained on Windows, future updates aim to support Linux and MacOS.

- **Remote Dependencies:** Automate your builds and other developer's by setting up your repository's `.r3make` directory, and leveraging the `gitdeps` pre build command. (Scroll down for more info on `remote dependencies`.)

<br>

## Installation

Install via [PyPI](https://pypi.org/project/r3make):

```bash
pip install r3make
```

<br>

## Getting Started

### Step 1. Create a `r3make` Configuration File

The `r3make` file uses JSON to specify project settings. Here's a blank r3make configuration in its entirety:

```json
{
   "c-instance": "GCC",
    "c-targets": {
      "my_lib":{
         "r3make": {
             "flags": [],
             "pre-build": {},
             "post-build": {}
         },
         "c-flags": [],
         "c-defines": [],
         "src-dirs": [],
         "src-files": [],
         "inc-dirs": [],
         "lib-links": {},
         "out-dir": "bin",
         "out-type": "exe",
         "out-name": "program"
      }
    }
}
```

- **(Optional) `r3make`**: Dictionary of pre and post/build commands, and build flags for a target.
- **`c-instance`**: Compiler to use (currently supported: GCC, CLANG, EMCC).
- **`c-targets`**: Compilation targets for your project.
- **(Optional) `c-flags`**: List of compiler flags to be used during this build.
- **(Optional) `c-deines`**: List of project directives to be defined by the pre-processor.
- **`inc-dirs`**: List of directories to search for header files.
- **`src-dirs`**: Directories containing source files.
- **(Optional) `src-files`**: A list containing string paths to source files.
- **(Optional) `lib-links`**: Key-value pairs of libraries to link. Value is optional for default system paths.
- **`out-dir`**: Directory for generated output.
- **`out-type`**: Type of output file (`exe`, `dll`, `a`, etc.).
- **`out-name`**: Name of the output file (without extension).

<br>

### Step 2. Build Your Project

Run the following command in the same directory as your `r3make` configuration file:

```bash
r3make {target}
```

This will compile and link the specified compilation `{target}`, placing the output in the specified `out-dir`.

<br>

## Example Usage

Given the following directory structure:

```
MyProject/
src/
   /main.c
   /utils.c
tests/
   /test_main.c
   /test_utils.c
include/
       /utils.h
r3make
```

A `r3make` configuration would look like this:
```json
{
   "c-instance": "GCC",
   "c-targets": {
      "MyProject": {
         "src-dirs": ["src"],
         "inc-dirs": ["include"],
         "out-dir": "bin",
         "out-type": "exe",
         "out-name": "MyProject"
      },
      "tests": {
         "r3make": {
             "flags": ["buildeach"],
             "post-build": {
                 "nofiles": null
             }
         },
         "src-dirs": ["tests"],
         "inc-dirs": ["include"],
         "out-type": "exe",
         "out-name": null,
         "out-dir": "bin"
        }
   }
}
```

You would then run the following command: `r3make MyProject`

This configuration will:
1. Compile `main.c` and `utils.c` into object files.
2. Link them into an executable called `MyProject.exe` in the `bin` directory.

Notice that there are two targets within this configuration, the tests target can be built using the following command: `r3make tests`  
The `tests` target makes use of the `buildeach` r3make flag, which tells r3make to compile each of the source files for this target individually. (the output will be named after the source.)
1. Compile `test_main.c` and `test_utils.c` into object files.
2. Link them each into executables named `test_main.exe` and `test_utils.exe` in the `bin` directory.

>Note: r3make will create and store object files at `config[out-dir]\\ofiles`. This directory can be safely removed after a build has completed either manually or with the `nofiles` post-build command.

<br>

## Remote Dependencies With r3make
> Note: Any dependency left with a path value of `null` in the configuration will be searched for (recursively) in the current working directory, then OS specific library locations, and finally the default search locations of your selected compiler instance. (System libraries like opengl32 dont require a path to be specified.)

r3make supports a configuration field named after the tool `r3make`. This field is used to invoke r3make `pre-build` and `post-build` commands, thus these are the field names of the `r3make` fields.

A Valid `r3make` field might look like this:
```json
{
   ...
   "r3make": {
      "pre-build": {
         "command1": null,
         "command2": "path/to/some/asset",
      },
      "post-build": {
         "command5": [1, 2, 3],
      }
   }
}
```
As you can see, r3make commands may be passed parameters of different types, so make sure you research the command you are using, and the parameters expected!
> Note: all r3make commands take both the calling configuration along with the value attached to the command field.

### How does this help further automate a build?
r3make has the ability to clone and build dependencies from Github, and making a project available to the CLI is as simple as the following:

In the root of your project's repository, create a directory named `.r3make`.

Next simply add your project's `r3make` configuration into this directory.

Commit and push the changes, and thats it!

<br>

### How about fetching these dependencies as the end-user?
Thats simple too, just add the *remote-hosted* dependency to your project's `.r3make` configuration like so:

```json
{
   ...
   "lib-links": {
      "somelib": null
   }
}
```
> Note: For fetched dependencies its advised to set the path to the dependency as `null` for your `lib-links` field as it will be cloned to and built in an OS default library path. (The compiler/CLI will be able to find it.)

After that, just add the `gitdeps` command to your `r3make`: `pre-build` field! The `gitdeps` command expects a list of strings as a parameter. These strings should be the `author`/`dep` of your dependency.

Following the above should yield these fields:

```json
{
   ...
   "r3make": {
      "pre-build": {
         "gitdeps": ["someguy/somelib"],
      }
   }
}
```

Now your all set, and ready to build!
> Note: The `gitdeps` command clones dependencies into a default library path based on your operating system. This command may fail if your OS requires admin privileges to read/write to this directory!

<br>

## Why r3make?

While tools like CMake are powerful, they can be overly complex for straightforward tasks, and Makefiles tend to be 'not so readable'. r3make focuses on simplicity and ease of use, letting you get back to writing code rather than managing build configurations.

<br>

## r3make's Wishlist

1. **Improved Error Handling**:
   - Provide more descriptive errors when builds fail.
   - Catch common misconfigurations in the `r3make` file.

2. **Incremental Builds**:
   - Implement a mechanism to skip recompilation of unchanged files.

3. **Verbose Mode**:
   - Add a CLI flag for detailed logging of compilation steps.

4. **Parallel Builds**:
   - Utilize multiple CPU cores to speed up compilation.

<br>

## r3make Contributors


<a href="https://github.com/r3shape/r3make/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=r3shape/r3make&max=500&columns=20&anon=1" />
</a>

<br>

Contributions are welcome! If you encounter issues or have feature suggestions, feel free to open an issue or submit a pull request on GitHub.

<br>

## License

r3make is licensed under the MIT License. See `LICENSE` for more information.
