# EntropyMax Windows installer build (installer/)

This directory is a build output for the NSIS installer. It is safe to delete and regenerate at any time. Source code lives outside of this directory.

Layout
- CMakeCache.txt, CMakeFiles/, *.vcxproj, *.sln: Generated build files
- stage/:
  - bin/: Built executables and bundled DLLs (e.g., run_entropymax.exe, Arrow/Parquet DLLs)
  - lib/: Static libraries (e.g., entropymax.lib, parquet_io.lib)
- Release/:
  - EntropyMax Backend-<version>-win64.exe: NSIS installer (primary artifact)
  - EntropyMax Backend-<version>-win64.zip: Zip package (secondary artifact)
- _CPack_Packages/: Temporary packaging area created by CPack

What to run
- Primary artifact: `Release/EntropyMax Backend-0.1.0-win64.exe`
  - Installs to `Program Files\EntropyMax Backend` by default
  - Adds `$INSTDIR\bin` to PATH (Arrow/Parquet DLLs available)
  - Optionally creates a desktop shortcut to the install folder

Rebuilding here
```bash
# Configure (Arrow via vcpkg toolchain)
cmake -S backend -B installer \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="third_party/vcpkg/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_TARGET_TRIPLET=x64-windows

# Build and package
cmake --build installer --config Release --target PACKAGE
```

Notes
- Do not rename this directory after generation; it contains absolute paths. Instead, delete and reconfigure if needed.
- The installer bundles Arrow/Parquet DLLs from vcpkg when available and ensures they are reachable via PATH.
