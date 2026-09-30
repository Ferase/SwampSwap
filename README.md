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

This project does not utilize any of croc's source code, however releases of this project from **v1.5** onwards do bundle croc binaries.

## Installing

Swamp Swap bundles the croc binaries from [this release](https://github.com/schollz/croc/releases/tag/v11.5.4) of the program. Thus, you won't need to manually download or install croc for your system.

However, if you have croc installed on your system via a package manager (`winget`, `apt`, `dnf`, `zypper`, `pacman`, or `apk` acording to croc's [official repository](https://github.com/schollz/croc/releases/latest)), you can enable the option **Use system croc** in **Settings > croc > Use system croc** to make Swamp Swap use that version of croc instead of the one bundled within itself. This isn't generally recommended, as croc updates can sometimes include changes that will break some functionality of Swamp Swap.

### On Windows

1. Extract **SwampSwap_Windows_x86_64.zip** anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
2. Enter the extracted folder, and open **SwampSwap.exe**
3. You will be prompted to set up the program.

### macOS

1. Extract the **.tar.gz** file anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
2. Enter the extracted folder, and open the file **SwampSwap**
3. You will be prompted to set up the program.

### Linux

1. Go to the [releases page for Swamp Swap](https://github.com/Ferase/SwampSwap/releases/latest) and download one of these four files depending on your system architecture and prefeerence:
    - **SwampSwap_Linux_x86_64.tar.gz** (Intel processor, archive containing executable)
    - **SwampSwap_Linux_x86_64.AppImage** (Intel processor, full AppImage)
2. If you downloaded an **.tar.gz** file:
    1. Extract the **.tar.gz** file anywhere you'd like (Note: this is the actual program, not an installer, so extract it wherever you would most easily be able to use it from)
    2. Enter the extracted folder, and open the file **SwampSwap**
3. If you downloaded an **AppImage**:
    1. Save the AppImage into your downloads folder (or anywhere you can easily get to it)
    2. Open a terminal wherever you saved the AppImage to, and make it executable
        ```
        chmod +x ./SwampSwap_Linux_x86_64.AppImage
        ```
    3. Then, run the install command:
        ```
        ./SwampSwap_Linux_x86_64.AppImage --install
        ```
    4. You should get a message that Swamp Swap was installed
    5. Open your application launcher and search for Swamp Swap, then run it
4. You will be prompted to set up the program.

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

This project is in no way affiliated with Zack Schollz or the croc project directly. This is purely a fun project that does not aim to (nor is capable of) replace croc or its functionality.