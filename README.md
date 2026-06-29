<div align="center">
    <img src="/images/SwampSwap_Icon.png" width="250px" border="0" alt="Swamp Swap icon">
    <br>
    <h1>Swamp Swap</h1>
</div>
<p align="center">A graphical user interface that controls the command line file transfer program <a href="https://github.com/schollz/croc" target="_blank">croc by Zack Shollz</a>.</p>
<div align="center" float="left">
    <img src="/images/SwampSwap_Window_ThemePink.png" width="250px" border="0" alt="Swamp Swap window preview with pink theme on the send tab">
    <img src="/images/SwampSwap_Window_ThemeDeepDark.png" width="250px" border="0" alt="Swamp Swap window preview with deep adark theme on the receive tab">
    <img src="/images/SwampSwap_Window_ThemeDark.png" width="250px" border="0" alt="Swamp Swap window preview with dark theme on the settings tab">
</div>

## Overview

This is a simple user interface that operates croc directly by constructing commands and executing them via `subprocess`. This project is intended to make working with croc a bit more interactive and give users that prefer GUIs a more convenient way to use the program.

This project does not use any code from croc and will not install it if you don't have it. Please visit <a href="https://github.com/schollz/croc" target="_blank">croc's repository</a> to see how to install it.

## Running

Simply visit the [Releases page](https://github.com/Ferase/SwampSwap/releases/latest) and download the version for your system.

Swamp Swap currently only supports **Linux** and **Windows**, however it can likely be built for your system if your OS supports Python.

## Known Issues

- Windows
    - Whenevr sending or receiving with croc, the program opens a command prompt window that must be preset to allow the GUI to pipe croc's output into itself. Without this window, the GUI cannot read what croc is doing. If anyone has any ideas on how to fix this, pelase let me know!
    - In some circumstances, the status text at the bottom left will disappear when running an operation.

## Building

Swamp Swap is built using PyInstaller, meaning you can only build for your own operating system and architecture. For example, if you build the program on Linux with an ARM processor, only other computers running Linux with an ARM processor can execute the program.

### Requirements

In order to build this Swamp Swap, you must have **Python 3.10**.

On Windows, you need the <a href="https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170" target="_blank">Microsoft C++ Redistributable</a>. On Linux, you will need to search for the C++ libraries for your distribution within your package manager.

When you build, you can use any of the four build scripts present in the root directory of the repository. Here's a breakdown of each:

- `build_onedir.spec` / Build the program to a directory with a single EXE and an `_internal` folder containing required binaries. *(This is how the releases were built)*
- `build_onedir_with_terminal.spec` / Build the program to a directory with a single EXE and an `_internal` folder containing required binaries. A terminal window will open alongside the program
- `build_onefile.spec` / Build the program to a single EXE file
- `build_onefile_with_terminal.spec` / Build the program to a single EXE file. A terminal window will open alongside the program

### Build Process

1. Clone the repository and enter the newly made directory in your terminal
```
git clone https://github.com/Ferase/SwampSwap
cd SwampSwap
```

2. Create a new virtual environment, then enter it
    1. On Windows:
    ```
    python -m venv venv
    venv\scripts\activate
    ```
    2. On Linux:
    ```
    python -m venv venv
    source venv/bin/activate
    ```

3. Ensure `pip` is up to date:
```
python -m pip install --upgrade pip
```

4. Install the required packages
```
pip install -r requirements.txt
```

5. Build the program
```
pyinstaller build_onedir.spec
```

## Credits

**User Interface**
- Ferase

**croc**
- [Zack Schollz](https://github.com/schollz)

**Testing**
- OctoToon

**Translations**
- Ferase (English)
- *Other translations to come*

## Disclaimer

This project is in no way affiliated with Zack Schollz or the croc project directly. This is purely a fun project that does not aim to (nor is capable of) replace croc or its functionality. It requires you have croc installed and will not install it for you.