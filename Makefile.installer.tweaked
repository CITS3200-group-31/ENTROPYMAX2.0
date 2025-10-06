SHELL := /bin/bash

.PHONY: all clean installer

all:
	cmake -S backend -B backend/build-msvc
	cmake --build backend/build-msvc --config Release --target run_entropymax

installer: all
	@echo "Building NSIS installer..."
	@"C:\\Progra~2\\NSIS\\Bin\\makensis.exe" installer\\EntropyMax.nsi || makensis installer\\EntropyMax.nsi

clean:
	rm -rf backend/build-msvc build/bin build/dlls


