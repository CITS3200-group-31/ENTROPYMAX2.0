# Packaging Guide

## Build Windows binary file

The following methods are used to output Windows x86 EXE files on computers with different architectures.

### On Windows

```
pacman -S mingw-w64-x86_64-gcc make
make runner
```

### On macOS

```
brew install mingw-w64
make windows
```

### On Linux

```
sudo apt install mingw-w64
make windows
```

## Prerequisites
- Python 3.11 environment with project dependencies: `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`: 
    - Do not add it to requirements.txt, as this may cause inexplicable errors.
- run_entropymax:
    - frontend/run_entropymax is the v1.1 version for macOS ARM  
    - frontend/run_entropymax.exe is the binary file for Windows x86  
    - Before starting, please ensure that both files are in the directory. If there are any updates to the C Binary File in the future, simply replace them with the same filenames.

## macOS build
1. Activate the project environment.
2. From `frontend/`, run:
	```bash
	./build_macos.sh
	```
3. Output: `dist/EntropyMax.app`

## Windows build
1. Activate the project environment (PowerShell or CMD).
2. From `frontend\`, run:
	```powershell
	.\build_win.sh
	```
3. Output: `dist/EntropyMax.exe`

## Cache location (runtime)
- macOS: `~/Library/Application Support/EntropyMax/entro_cache`
- Windows: `%LOCALAPPDATA%\EntropyMax\entro_cache`
- If need override cache location: set `ENTROPYMAX_CACHE_DIR` before launching the app.

## Verification
- Launch the produced build and confirm analysis runs end-to-end.
- Check the cache folder above for session files after a run