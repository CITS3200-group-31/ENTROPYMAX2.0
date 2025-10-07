.PHONY: all installer clean frontend copy
SHELL := cmd
.SHELLFLAGS := /C

all:
	cmake -S backend -B backend/build-msvc
	cmake --build backend/build-msvc --config Release --target run_entropymax
	cmake -E make_directory build/bin
	cmake -E copy backend/build-msvc/Release/run_entropymax.exe build/bin/run_entropymax.exe

frontend: all
	@echo Building frontend app...
	@if not exist frontend\main.py ( echo No frontend\main.py, skipping frontend build & exit /B 0 )
	@cmake -E copy build/bin/run_entropymax.exe frontend/run_entropymax.exe
	@cd frontend && py -3 -m pip install -U pip
	@cd frontend && py -3 -m pip install -r requirements.txt
	@cd frontend && py -3 -m pip install pyinstaller
	@cd frontend && ( if exist win.spec ( py -3 -m PyInstaller --clean -y win.spec ) else ( py -3 -m PyInstaller --clean -y --noconsole --onefile --name EntropyMax main.py ) )
	@echo Copying latest frontend build artifact to build\EntropyMax.exe
	@powershell -NoProfile -Command "$src = Get-ChildItem -Path 'frontend\\dist' -Recurse -Filter 'EntropyMax.exe' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($null -ne $src) { New-Item -ItemType Directory -Force -Path 'build' | Out-Null; Copy-Item -Force $src.FullName 'build\\EntropyMax.exe'; Write-Output \"Copied $($src.FullName) -> build\\EntropyMax.exe\" } else { Write-Output 'No frontend executable found under frontend\\dist; skipping copy.' }"
	@if exist build\EntropyMax.exe ( echo Frontend staged: build\EntropyMax.exe ) else ( echo Frontend EXE missing. Frontend build failed. & exit /B 1 )

installer: all copy
	@echo Building NSIS installer...
	@"C:\\Progra~2\\NSIS\\Bin\\makensis.exe" /DPROJ_ROOT="$(CURDIR)" installer\\EntropyMax.nsi || makensis /DPROJ_ROOT="$(CURDIR)" installer\\EntropyMax.nsi

copy:
	@echo Copying entire frontend\\dist to build
	@if not exist build mkdir build
	@xcopy /E /I /Y "C:\\Users\\unixthat\\coding\\ENTROPYMAX2.0\\frontend\\dist\\*" "build\\" >NUL

ifeq ($(OS),Windows_NT)
clean:
	- if exist backend\\build-msvc rmdir /S /Q backend\\build-msvc
	- if exist build\\bin rmdir /S /Q build\\bin
else
clean:
	- rm -rf backend/build-msvc build/bin
endif


