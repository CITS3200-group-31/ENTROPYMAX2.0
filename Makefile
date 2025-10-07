.PHONY: all installer clean frontend

all:
	cmake -S backend -B backend/build-msvc
	cmake --build backend/build-msvc --config Release --target run_entropymax
	cmake -E make_directory build/bin
	cmake -E copy backend/build-msvc/Release/run_entropymax.exe build/bin/run_entropymax.exe

frontend: all
	cmake -E copy build/bin/run_entropymax.exe frontend/run_entropymax.exe
	cd frontend && py -3.11 -m PyInstaller --clean -y win.spec

installer:
	@$(MAKE) clean
	@$(MAKE) all
	@echo "Building NSIS installer..."
	@"C:\\Progra~2\\NSIS\\Bin\\makensis.exe" /DPROJ_ROOT="$(CURDIR)" installer\\EntropyMax.nsi || makensis /DPROJ_ROOT="$(CURDIR)" installer\\EntropyMax.nsi

ifeq ($(OS),Windows_NT)
clean:
	- if exist backend\\build-msvc rmdir /S /Q backend\\build-msvc
	- if exist build\\bin rmdir /S /Q build\\bin
else
clean:
	- rm -rf backend/build-msvc build/bin
endif


