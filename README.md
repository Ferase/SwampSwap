<div align="center">
    <img src="/images/SwampSwap_Icon.png" width="250px" border="0" alt="Swamp Swap icon">
    <br>
    <h1>Swamp Swap</h1>
</div>
<p align="center">A graphical user interface that controls the command line file transfer program <a href="https://github.com/schollz/croc" target="_blank">croc by Zack Shollz</a>.</p>
<div align="center" float="left">
    <img src="/assets/gif/wait_for_peer.gif" width="250px" border="0" alt="croc and bird sending files">
    <img src="/assets/gif/idle.gif" width="250px" border="0" alt="croc and bird waiting idle">
    <img src="/assets/gif/connecting_to_peer.gif" width="250px" border="0" alt="croc and bird looking for files to receive">
</div>
<div align="center" float="left">
    <img src="/images/SwampSwap_Window_Screenshot_01.png" width="250px" border="0" alt="Swamp Swap window preview with pink theme on the send tab">
    <img src="/images/SwampSwap_Window_Screenshot_02.png" width="250px" border="0" alt="Swamp Swap window preview with deep adark theme on the receive tab">
    <img src="/images/SwampSwap_Window_Screenshot_03.png" width="250px" border="0" alt="Swamp Swap window preview with dark theme on the settings tab">
</div>

## Overview

This is a simple user interface that operates croc directly by constructing commands and executing them via `subprocess`. This project is intended to make working with croc a bit more interactive and give users that prefer GUIs a more convenient way to use the program.

This project does not use any code from croc and will not install it if you don't have it. Please visit <a href="https://github.com/schollz/croc" target="_blank">croc's repository</a> to see how to install it.

## Installing

Before installing Swamp Swap, you must install croc for your system. Brief instructions will be given below for Windows due to the convineicne of `winget`, but you should refer to the [official install guide](https://github.com/schollz/croc#install) for all other systems since there are several distributions and package managers on which croc is available for macOS, Linux, Conda, Docker, and more.

Note that you can also obtain releases from [croc's releases page](https://github.com/schollz/croc/releases/latest) and use those instead of anything from any of the package managers, though it's not as convenient as getting ti from a package manager and could requrie advanced setup for your system in certain cases.

### On Windows

1. Open your command prompt and use `winget`, the pre-installed Windows package manager, to install croc from the official Windows repository:
    ```
    winget install schollz.croc
    ```
    - If you are running `winget` for the first time, it will ask you to agree to their policies. Press `y` for everything to proceed
    - If you already have croc installed via `winget`, you can update it/check for updates by doing:
        ```
        winget upgrade schollz.croc
        ```
2. Once croc is installed, go to the [releases page for Swamp Swap](https://github.com/Ferase/SwampSwap/releases/latest) and downlaod **SwampSwap_Windows_x86_64.zip**
3. Extract **SwampSwap_Windows_x86_64.zip** anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
4. Enter the extracted folder, and open **SwampSwap.exe**
5. You will be prompted to set up the program
6. It should launch!

### macOS

According to the [official install guide](https://github.com/schollz/croc#install), croc is available via `brew` and `port`. See the official install guide for more.

1. After installing croc, go to the [releases page for Swamp Swap](https://github.com/Ferase/SwampSwap/releases/latest) and download either **SwampSwap_macOS_x86_64.tar.gz** (Intel processors) or **SwampSwap_macOS_arm64.tar.gz** (ARM/Apple processors) based on your system's architecture.
2. Extract the **.tar.gz** file anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
4. Enter the extracted folder, and open the file **SwampSwap**
5. You will be prompted to set up the program
6. It should launch!

### Linux

Please refer to the [official install guide](https://github.com/schollz/croc#install) for info on installing croc for your Linux distribution/package manager.

1. After installing croc, go to the [releases page for Swamp Swap](https://github.com/Ferase/SwampSwap/releases/latest) and download one of these four files depending on your system architecture and prefeerence:
    - **SwampSwap_Linux_x86_64.tar.gz** (Intel processor, archive containing executable)
    - **SwampSwap_Linux_aarch64.tar.gz** (ARM64 processor, archive containing executable)
    - **SwampSwap_Linux_x86_64.AppImage** (Intel processor, full AppImage)
    - **SwampSwap_Linux_aarch64.AppImage** (ARM64 processor, full AppImage)
2. If you downloaded an **.tar.gz** file:
    1. Extract the **.tar.gz** file anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
    2. Enter the extracted folder, and open the file **SwampSwap**
3. If you downloaded an **AppImage**:
    1. Save the AppImage into your downloads folder (or anywhere you can easily get to it)
    2. Open a terminal wherever you saved the AppImage to, and make it executable
        ```
        chmod +x ./SwampSwap_Linux_YourArchHere.AppImage
        ```
    3. Then, run the install command:
        ```
        ./SwampSwap_Linux_YourArchHere.AppImage --install
        ```
    4. You should get a message that Swamp Swap was installed
    5. Open your application launcher and search for Swamp Swap, then run it
4. You will be prompted to set up the program
5. It should launch!

### Notes

I should also mention that sometimes new croc releases don't come out on all package managers at the same time they come out on GitHub. Thus, Swamp Swap may tell you **croc has a new version available**, but if that version doesn't get installed when you update your croc package on your OS, you can either install from GitHub directly (advanced) or wait until the new version comes out on your package manager. You can alternatively disable the update check in the **Settings** tab if you want to suppress the alert.

## Building

Swamp Swap is built using PyInstaller, meaning you can only build for your own operating system and architecture. For example, if you build the program on Linux with an ARM processor, only other computers running Linux with an ARM processor can execute the program.

### Requirements

In order to build Swamp Swap, you must have **Python 3.10+**.

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
- inktrinket

**Translations**
- Ferase (English)
- *Other translations to come*

## Disclaimer

This project is in no way affiliated with Zack Schollz or the croc project directly. This is purely a fun project that does not aim to (nor is capable of) replace croc or its functionality. It requires you have croc installed and will not install it for you.