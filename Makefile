# Minimal Makefile to build the backend runner

CC      ?= cc
CXX     ?= c++
CFLAGS  ?= -O2 -std=c11 -Wall -Wextra -Wpedantic
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Wpedantic
CPPFLAGS += -Ibackend/include -Ibackend/src/algo
# Enforce minimum language standard flags even if env overrides CFLAGS/CXXFLAGS
# Some environments predefine empty CFLAGS/CXXFLAGS, which would drop -std.
# Appending here guarantees the required standards remain in effect.
CFLAGS   += -std=c11
CXXFLAGS += -std=c++17
LDFLAGS ?=
LIBS    ?= -lm

BUILD_DIR := build
OBJ_DIR   := $(BUILD_DIR)/obj
BIN_DIR   := $(BUILD_DIR)/bin

RUNNER_SRC := backend/src/algo/run_entropymax.c
# Core C sources (always built)
CORE_SRCS_C := \
	backend/src/algo/preprocess.c \
	backend/src/algo/metrics.c \
	backend/src/algo/grouping.c \
	backend/src/algo/sweep.c \
	backend/src/util/util.c

# IO layer sources (conditional)
IO_SRC_C   := backend/src/io/parquet_stub.c
CORE_SRCS_CC :=

# -----------------------------------------------------------------------------
# Optional Arrow/Parquet (C++) support
# Define platform/paths early so detection works on re-parse invocations

UNAME_S := $(shell uname -s 2>/dev/null)
UNAME_M := $(shell uname -m 2>/dev/null)
VCPKG_ROOT ?= $(CURDIR)/third_party/vcpkg
# Triplet detection
ifeq ($(UNAME_S),Darwin)
  ifeq ($(UNAME_M),arm64)
    VCPKG_TRIPLET ?= arm64-osx
  else
    VCPKG_TRIPLET ?= x64-osx
  endif
else ifeq ($(UNAME_S),Linux)
  VCPKG_TRIPLET ?= x64-linux
else
  VCPKG_TRIPLET ?= x64-windows-static
endif

# Make vcpkg pkg-config discoverable if present
PKGCFG_VCPKG := $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib/pkgconfig
ifneq ($(wildcard $(PKGCFG_VCPKG)),)
  export PKG_CONFIG_PATH := $(PKGCFG_VCPKG):$(PKG_CONFIG_PATH)
endif

# If pkg-config finds arrow/parquet or vcpkg is installed, enable C++ path
HAVE_PKGCFG := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)

# CSV-only by default; set ENABLE_ARROW=1 to enable optional Arrow/Parquet path
ENABLE_ARROW ?= 0

ifeq ($(ENABLE_ARROW),1)
  HAVE_PKGCFG := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)
  # Prefer pkg-config
  ifeq ($(HAVE_PKGCFG),1)
    HAVE_ARROW := $(shell pkg-config --exists arrow parquet && echo 1 || echo 0)
  else
    HAVE_ARROW := 0
  endif
  # If not via pkg-config, check vcpkg installed path
  ifeq ($(HAVE_ARROW),0)
    ifneq ($(wildcard $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/include),)
      ARROW_CFLAGS := -I$(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/include
      ARROW_LIBS := -L$(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib -lparquet -larrow
      HAVE_ARROW := 1
      ifeq ($(UNAME_S),Darwin)
        LDFLAGS += -Wl,-rpath,@loader_path
      else ifeq ($(UNAME_S),Linux)
        LDFLAGS += -Wl,-rpath,'$$ORIGIN'
      endif
    endif
  endif
  ifeq ($(HAVE_ARROW),1)
    # Prefer pkg-config even when ARROW_CFLAGS was set from vcpkg
    ARROW_PKG_CFLAGS := $(shell pkg-config --cflags arrow parquet 2>/dev/null)
    ARROW_PKG_LIBS := $(shell pkg-config --libs arrow parquet 2>/dev/null)
    ifneq ($(strip $(ARROW_PKG_LIBS)),)
      CPPFLAGS += $(ARROW_PKG_CFLAGS) -DENABLE_ARROW
      LIBS += $(ARROW_PKG_LIBS)
    else
      CPPFLAGS += $(ARROW_CFLAGS) -DENABLE_ARROW
      # Manual fallback: include transitive deps commonly required by Arrow/Parquet
      LIBS += $(ARROW_LIBS)
    endif
    # Ensure transitive compression/RPC deps are linked (pkg-config may omit)
    LIBS += -lthrift -lre2 -lsnappy -lz -lzstd -llz4 -lbz2 -lbrotlienc -lbrotlidec -lbrotlicommon -lssl -lcrypto
    ifeq ($(UNAME_S),Linux)
      LIBS += -ldl
    endif
    CORE_SRCS_CC += backend/src/io/parquet_arrow.cc
    IO_SRC_C :=
  else
    $(warning Apache Arrow/Parquet dev libs not found; will build with stub IO.)
  endif
endif

# -----------------------------------------------------------------------------
# Sanitize library search paths: drop any -L<dir> that does not exist to avoid
# linker warnings like: "ld: warning: search path '<dir>' not found"
SANITIZED_LIBS := $(foreach tok,$(LIBS),$(if $(filter -L%,$(tok)),$(if $(wildcard $(patsubst -L%,%,$(tok))),$(tok),),$(tok)))
LIBS := $(SANITIZED_LIBS)

SANITIZED_LDFLAGS := $(foreach tok,$(LDFLAGS),$(if $(filter -L%,$(tok)),$(if $(wildcard $(patsubst -L%,%,$(tok))),$(tok),),$(tok)))
LDFLAGS := $(SANITIZED_LDFLAGS)

RUNNER_OBJ := $(OBJ_DIR)/backend/src/algo/run_entropymax.o
CORE_OBJS_C  := $(CORE_SRCS_C:%.c=$(OBJ_DIR)/%.o)
CORE_OBJS_CC := $(CORE_SRCS_CC:%.cc=$(OBJ_DIR)/%.o)
IO_OBJ_C     := $(IO_SRC_C:%.c=$(OBJ_DIR)/%.o)

RUNNER_BIN := $(BIN_DIR)/run_entropymax

.PHONY: all runner clean distclean

all: runner

runner: $(CORE_OBJS_C) $(CORE_OBJS_CC) $(IO_OBJ_C) $(RUNNER_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $(RUNNER_BIN) $(CORE_OBJS_C) $(CORE_OBJS_CC) $(IO_OBJ_C) $(RUNNER_OBJ) $(LDFLAGS) $(LIBS)
	@echo Built $(RUNNER_BIN)

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@


$(OBJ_DIR)/%.o: %.cc
	@mkdir -p $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

clean:
	@rm -rf $(BUILD_DIR)

distclean: clean
	@echo Clean complete

# -----------------------------------------------------------------------------
# Setup and dependency installation

.PHONY: setup setup-all deps arrow-deps arrow-auto pydeps

# High-level setup targets run sub-makes so that any newly generated config
# (e.g., vcpkg installs) is picked up on a fresh parse for the runner build.
setup:
	@$(MAKE) arrow-auto
	@$(MAKE) runner

deps: arrow-auto pydeps

UNAME_S := $(shell uname -s 2>/dev/null)
HAS_APT := $(shell command -v apt-get >/dev/null 2>&1 && echo 1 || echo 0)
HAS_BREW := $(shell command -v brew >/dev/null 2>&1 && echo 1 || echo 0)

arrow-deps:
ifeq ($(UNAME_S),Darwin)
ifeq ($(HAS_BREW),1)
	@echo "Installing Arrow/Parquet via Homebrew..."
	brew update && brew install apache-arrow || true
else
	@echo "Homebrew not found. Please install Homebrew and rerun make arrow-deps." && false
endif
else ifeq ($(UNAME_S),Linux)
ifeq ($(HAS_APT),1)
	@echo "Installing Arrow/Parquet dev libraries via apt-get..."
	sudo apt-get update -y && \
	sudo apt-get install -y libarrow-dev libparquet-dev || true
else
	@echo "Unknown Linux package manager. Please install Arrow dev libs (arrow, parquet) manually." && true
endif
else
	@echo "Windows or unknown OS: compiled Arrow not auto-installed. Use vcpkg or set ARROW_CFLAGS/ARROW_LIBS." && true
endif

# Auto-check Arrow via pkg-config, otherwise install via vcpkg
arrow-auto:
	@echo "Checking for Arrow/Parquet development libraries..."
	@if pkg-config --exists arrow parquet 2>/dev/null; then \
	  echo "Found Arrow via pkg-config."; \
	  exit 0; \
	fi; \
	if [ "$(UNAME_S)" = "Linux" ] && [ "$(HAS_APT)" = "1" ]; then \
	  echo "Installing Arrow/Parquet via apt-get..."; \
	  if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then \
	    DEBIAN_FRONTEND=noninteractive sudo -n apt-get update -y && \
	    DEBIAN_FRONTEND=noninteractive sudo -n apt-get install -y libarrow-dev libparquet-dev pkg-config cmake ninja-build g++ curl zip unzip tar flex bison || true; \
	  elif command -v sudo >/dev/null 2>&1; then \
	    if [ -t 1 ]; then \
	      sudo apt-get update -y && sudo apt-get install -y libarrow-dev libparquet-dev pkg-config cmake ninja-build g++ curl zip unzip tar flex bison || true; \
	    else \
	      echo "sudo requires a password but no TTY is available. Please run:"; \
	      echo "  sudo apt-get update -y && sudo apt-get install -y libarrow-dev libparquet-dev pkg-config cmake ninja-build g++ curl zip unzip tar flex bison"; \
	    fi; \
	  elif [ "$$(id -u)" = "0" ]; then \
	    DEBIAN_FRONTEND=noninteractive apt-get update -y && \
	    DEBIAN_FRONTEND=noninteractive apt-get install -y libarrow-dev libparquet-dev pkg-config cmake ninja-build g++ curl zip unzip tar flex bison || true; \
	  else \
	    echo "sudo not found. Please run as root:"; \
	    echo "  apt-get update -y && apt-get install -y libarrow-dev libparquet-dev pkg-config cmake ninja-build g++ curl zip unzip tar flex bison"; \
	  fi; \
	  if pkg-config --exists arrow parquet; then \
	    echo "Installed Arrow via apt-get."; \
	    exit 0; \
	  fi; \
	fi; \
	if [ "$(UNAME_S)" = "Darwin" ] && [ "$(HAS_BREW)" = "1" ]; then \
	  echo "Installing Arrow/Parquet via Homebrew..."; \
	  brew update && brew install apache-arrow || true; \
	  if pkg-config --exists arrow parquet; then \
	    echo "Installed Arrow via Homebrew."; \
	    exit 0; \
	  fi; \
	fi; \
	if [ "$(UNAME_S)" = "Darwin" ] && [ "$(HAS_BREW)" != "1" ]; then \
	  echo "Homebrew not found. Installing Homebrew..."; \
	  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || true; \
	  eval "$$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || eval "$$(/usr/local/bin/brew shellenv)" 2>/dev/null || true; \
	  echo "Installing Arrow/Parquet via Homebrew..."; \
	  brew update && brew install apache-arrow || true; \
	  if pkg-config --exists arrow parquet; then \
	    echo "Installed Arrow via Homebrew (post-install)."; \
	    exit 0; \
	  fi; \
	fi; \
	echo "Arrow not available via system package manager. Using vcpkg..."; \
	$(MAKE) bootstrap-vcpkg; \
	cd $(VCPKG_ROOT) && git pull || true; \
	"$(VCPKG_ROOT)/vcpkg" update || true; \
	if ! "$(VCPKG_ROOT)/vcpkg" install arrow[parquet]:$(VCPKG_TRIPLET); then \
	  echo "vcpkg install failed, attempting clean and retry..."; \
	  rm -rf "$(VCPKG_ROOT)/packages/arrow_$(VCPKG_TRIPLET)" "$(VCPKG_ROOT)/buildtrees/arrow" "$(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/share/arrow/vcpkg_abi_info.txt" || true; \
	  "$(VCPKG_ROOT)/vcpkg" remove --recurse arrow:$(VCPKG_TRIPLET) || true; \
	  "$(VCPKG_ROOT)/vcpkg" install arrow[parquet]:$(VCPKG_TRIPLET) || { echo "vcpkg install failed after cleanup"; exit 2; }; \
	fi;

pydeps:
	@echo "Setting up Python venv and installing pyarrow/pandas..."
	python3 -m venv .venv || true
	. ./.venv/bin/activate && pip install -U pip && pip install pyarrow pandas || true

# -----------------------------------------------------------------------------
# vcpkg bootstrap and Arrow install (static on Windows, shared on macOS/Linux)

VCPKG_ROOT ?= $(CURDIR)/third_party/vcpkg
UNAME_S := $(shell uname -s 2>/dev/null)
UNAME_M := $(shell uname -m 2>/dev/null)

.PHONY: bootstrap-vcpkg arrow-vcpkg bundle-linux bundle-macos bundle-windows bundle

bootstrap-vcpkg:
	@mkdir -p third_party && test -d $(VCPKG_ROOT) || git clone https://github.com/microsoft/vcpkg.git $(VCPKG_ROOT)
	@echo "Bootstrapping vcpkg..."

ifeq ($(UNAME_S),Linux)
	@if [ "$(HAS_APT)" = "1" ]; then \
	  echo "Ensuring curl/zip/unzip/tar/flex/bison/pkg-config/cmake/ninja/g++ are installed..."; \
	  if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then \
	    DEBIAN_FRONTEND=noninteractive sudo -n apt-get update -y && \
	    DEBIAN_FRONTEND=noninteractive sudo -n apt-get install -y curl zip unzip tar flex bison pkg-config cmake ninja-build g++; \
	  elif command -v sudo >/dev/null 2>&1; then \
	    if [ -t 1 ]; then \
	      sudo apt-get update -y && sudo apt-get install -y curl zip unzip tar flex bison pkg-config cmake ninja-build g++; \
	    else \
	      echo "sudo requires a password but no TTY is available. Please run:"; \
	      echo "  sudo apt-get update -y && sudo apt-get install -y curl zip unzip tar flex bison pkg-config cmake ninja-build g+"; \
	    fi; \
	  elif [ "$$(id -u)" = "0" ]; then \
	    DEBIAN_FRONTEND=noninteractive apt-get update -y && \
	    DEBIAN_FRONTEND=noninteractive apt-get install -y curl zip unzip tar flex bison pkg-config cmake ninja-build g++; \
	  else \
	    echo "sudo not found. Please run as root:"; \
	    echo "  apt-get update -y && apt-get install -y curl zip unzip tar flex bison pkg-config cmake ninja-build g+"; \
	  fi; \
	fi
	@cd $(VCPKG_ROOT) && ./bootstrap-vcpkg.sh
else ifeq ($(UNAME_S),Darwin)
	@cd $(VCPKG_ROOT) && ./bootstrap-vcpkg.sh
else
	@cd $(VCPKG_ROOT) && ./bootstrap-vcpkg.bat
endif
	@([ -x "$(VCPKG_ROOT)/vcpkg" ] || [ -x "$(VCPKG_ROOT)/vcpkg.exe" ]) || (echo "vcpkg bootstrap failed" && false)

# Triplet detection
ifeq ($(UNAME_S),Darwin)
  ifeq ($(UNAME_M),arm64)
    VCPKG_TRIPLET ?= arm64-osx
  else
    VCPKG_TRIPLET ?= x64-osx
  endif
else ifeq ($(UNAME_S),Linux)
  VCPKG_TRIPLET ?= x64-linux
else
  VCPKG_TRIPLET ?= x64-windows-static
endif


arrow-vcpkg: bootstrap-vcpkg
	@echo "Installing Arrow/Parquet via vcpkg for $(VCPKG_TRIPLET)..."
	@"$(VCPKG_ROOT)/vcpkg" install arrow[parquet]:$(VCPKG_TRIPLET)
	@echo "Setting ARROW_CFLAGS/ARROW_LIBS from vcpkg installed tree"
	@echo "Note: export ARROW_CFLAGS and ARROW_LIBS or pass as make variables for subsequent builds."
	@echo "ARROW_CFLAGS=-I$(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/include"
	@echo "ARROW_LIBS=-L$(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib -lparquet -larrow"

# -----------------------------------------------------------------------------
# Bundle targets to produce redistributable artifacts with libs

DIST_DIR := dist
BIN_NAME := run_entropymax

bundle: bundle-linux bundle-macos bundle-windows

bundle-linux:
ifeq ($(UNAME_S),Linux)
	@echo "Bundling Linux artifact..."
	@mkdir -p $(DIST_DIR)/linux
	@cp $(BUILD_DIR)/bin/$(BIN_NAME) $(DIST_DIR)/linux/
	@echo "Copying Arrow/Parquet shared libs (if present)..."
	-ldd $(BUILD_DIR)/bin/$(BIN_NAME) | awk '/arrow|parquet/ {print $$3}' | xargs -r -I{} cp -n {} $(DIST_DIR)/linux/
	@echo "Copying vcpkg Arrow/Parquet libs (if available)..."
	-test -d $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib && cp -n $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib/libarrow*.so* $(DIST_DIR)/linux/ 2>/dev/null || true
	-test -d $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib && cp -n $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib/libparquet*.so* $(DIST_DIR)/linux/ 2>/dev/null || true
	@echo "Done: $(DIST_DIR)/linux"
endif

bundle-macos:
ifeq ($(UNAME_S),Darwin)
	@echo "Bundling macOS artifact..."
	@mkdir -p $(DIST_DIR)/macos
	@cp $(BUILD_DIR)/bin/$(BIN_NAME) $(DIST_DIR)/macos/
	@echo "Copying Arrow/Parquet dylibs (if present)..."
	-otool -L $(BUILD_DIR)/bin/$(BIN_NAME) | awk '/arrow|parquet/ {print $$1}' | grep \/usr\/local\|\/opt\|vcpkg || true
	-otool -L $(BUILD_DIR)/bin/$(BIN_NAME) | awk '/arrow|parquet/ {print $$1}' | xargs -I{} cp -n {} $(DIST_DIR)/macos/ 2>/dev/null || true
	@echo "Copying vcpkg Arrow/Parquet dylibs (if available)..."
	-test -d $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib && cp -n $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib/libarrow*.dylib $(DIST_DIR)/macos/ 2>/dev/null || true
	-test -d $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib && cp -n $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib/libparquet*.dylib $(DIST_DIR)/macos/ 2>/dev/null || true
	@echo "Fixing rpath to @loader_path..."
	-install_name_tool -add_rpath @loader_path $(DIST_DIR)/macos/$(BIN_NAME) 2>/dev/null || true
	@echo "Done: $(DIST_DIR)/macos"
endif

bundle-windows:
	@echo "Bundling Windows artifact (copy DLLs next to EXE if built on Windows)..."
	@mkdir -p $(DIST_DIR)/windows
	@cp -f $(BUILD_DIR)/bin/$(BIN_NAME) $(DIST_DIR)/windows/ 2>/dev/null || true
	@echo "Copying vcpkg Arrow/Parquet DLLs (if available)..."
	-if exist "$(VCPKG_ROOT)\installed\$(VCPKG_TRIPLET)\bin" copy /Y "$(VCPKG_ROOT)\installed\$(VCPKG_TRIPLET)\bin\arrow*.dll" "$(DIST_DIR)\windows\" >NUL 2>&1
	-if exist "$(VCPKG_ROOT)\installed\$(VCPKG_TRIPLET)\bin" copy /Y "$(VCPKG_ROOT)\installed\$(VCPKG_TRIPLET)\bin\parquet*.dll" "$(DIST_DIR)\windows\" >NUL 2>&1

# -----------------------------------------------------------------------------
# Frontend (Python) setup and run

.PHONY: frontend-deps frontend-run frontend-test

frontend-deps:
	@echo "Setting up frontend venv and installing requirements..."
	python3 -m venv frontend/.venv || true
	. frontend/.venv/bin/activate && pip install -U pip && pip install -r frontend/requirements.txt

frontend-run:
	@echo "Running frontend main.py..."
	. frontend/.venv/bin/activate && python frontend/main.py

frontend-test:
	@echo "Running frontend tests..."
	. frontend/.venv/bin/activate && python -m pytest -q frontend/test || true

# -----------------------------------------------------------------------------
# Frontend Linux runtime setup and launcher

.PHONY: frontend-linux-setup frontend-launch-linux

# Common runtime packages for Qt WebEngine on Ubuntu/WSL
FRONTEND_LINUX_DEPS := \
  libxcb-cursor0 libxkbcommon-x11-0 libxcb-xinerama0 libxkbfile1 \
  libnss3 libnspr4 libxcomposite1 libxrandr2 libxdamage1 libxkbcommon0 \
  libgbm1 libasound2t64 libxtst6 libx11-xcb1 libxcb-xkb1 libxcb-icccm4 \
  libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxshmfence1 libegl1 \
  libgl1-mesa-dri mesa-vulkan-drivers fonts-dejavu-core fonts-liberation

frontend-linux-setup:
ifeq ($(UNAME_S),Linux)
ifeq ($(HAS_APT),1)
	@echo "Installing Qt WebEngine runtime libraries via apt-get..."
	@if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then \
	  DEBIAN_FRONTEND=noninteractive sudo -n apt-get update -y && \
	  DEBIAN_FRONTEND=noninteractive sudo -n apt-get install -y $(FRONTEND_LINUX_DEPS) || true; \
	elif command -v sudo >/dev/null 2>&1; then \
	  if [ -t 1 ]; then \
	    sudo apt-get update -y && sudo apt-get install -y $(FRONTEND_LINUX_DEPS) || true; \
	  else \
	    echo "sudo requires a password but no TTY is available. Please run:"; \
	    echo "  sudo apt-get update -y && sudo apt-get install -y $(FRONTEND_LINUX_DEPS)"; \
	  fi; \
	elif [ "$$("id" -u)" = "0" ]; then \
	  DEBIAN_FRONTEND=noninteractive apt-get update -y && \
	  DEBIAN_FRONTEND=noninteractive apt-get install -y $(FRONTEND_LINUX_DEPS) || true; \
	else \
	  echo "sudo not found. Please run as root:"; \
	  echo "  apt-get update -y && apt-get install -y $(FRONTEND_LINUX_DEPS)"; \
	fi
else
	@echo "Non-apt Linux distro detected. Please install WebEngine runtime libs equivalent to: $(FRONTEND_LINUX_DEPS)" && true
endif
else
	@echo "frontend-linux-setup is only for Linux." && true
endif

frontend-launch-linux: frontend-deps
	@echo "Creating Linux launcher script..."
	@mkdir -p bin
	@printf '%s\n' '#!/usr/bin/env bash' \
	  'set -euo pipefail' \
	  'SCRIPT_DIR="$$(cd "$$(dirname "$$0")" && pwd)"' \
	  'ROOT_DIR="$${SCRIPT_DIR%/bin}"' \
	  'VENV_DIR="$$ROOT_DIR/frontend/.venv"' \
	  'if [ ! -f "$$VENV_DIR/bin/activate" ]; then' \
	  '  echo "Frontend venv missing. Run: make frontend-deps"; exit 1; fi' \
	  'source "$$VENV_DIR/bin/activate"' \
	  'export QTWEBENGINE_DISABLE_SANDBOX=1' \
	  'if [ -n "$$WAYLAND_DISPLAY" ]; then' \
	  '  export QT_QPA_PLATFORM=wayland' \
	  '  export QT_OPENGL=desktop' \
	  '  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --ozone-platform=wayland"' \
	  'else' \
	  '  export QT_QPA_PLATFORM=xcb' \
	  '  export QT_OPENGL=desktop' \
	  '  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"' \
	  'fi' \
	  'python "$$ROOT_DIR/frontend/main.py" || {' \
	  '  echo "Primary launch failed, retrying with software rendering..."; ' \
	  '  export QT_OPENGL=software; export QSG_RHI_BACKEND=software; export LIBGL_ALWAYS_SOFTWARE=1; export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe;' \
	  '  export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --disable-gpu-compositing --in-process-gpu --single-process --no-zygote --disable-software-rasterizer";' \
	  '  python "$$ROOT_DIR/frontend/main.py"; }' \
	  > bin/run-frontend-linux.sh
	@chmod +x bin/run-frontend-linux.sh

# Convenience: full stack setup
setup-all:
	@$(MAKE) arrow-auto
	@$(MAKE) frontend-deps
	@$(MAKE) runner


