# Minimal Makefile to build the backend runner

CC      ?= cc
CFLAGS  ?= -O2 -std=c11 -Wall -Wextra -Wpedantic
CPPFLAGS += -Ibackend/include -Ibackend/src/algo
LDFLAGS ?=
LIBS    ?= -lm

BUILD_DIR := build
OBJ_DIR   := $(BUILD_DIR)/obj
BIN_DIR   := $(BUILD_DIR)/bin

RUNNER_SRC := backend/src/algo/run_entropymax.c
CORE_SRCS  := \
	backend/src/algo/preprocess.c \
	backend/src/algo/metrics.c \
	backend/src/algo/grouping.c \
	backend/src/algo/sweep.c \
	backend/src/util/util.c \
	backend/src/io/csv_stub.c

# -----------------------------------------------------------------------------
# Optional Arrow/Parquet (C++) support
# If pkg-config finds arrow and parquet, enable compiled Parquet path.
# You can also force with ENABLE_ARROW=1 and provide ARROW_LIBS/ARROW_CFLAGS.

HAVE_PKGCFG := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)
ifeq ($(ENABLE_ARROW),1)
CPPFLAGS += $(ARROW_CFLAGS)
CORE_SRCS += backend/src/io/parquet_arrow.cc
LIBS += $(ARROW_LIBS)
CPPFLAGS += -DENABLE_ARROW
else
ifeq ($(HAVE_PKGCFG),1)
HAVE_ARROW := $(shell pkg-config --exists arrow parquet && echo 1 || echo 0)
ifeq ($(HAVE_ARROW),1)
CPPFLAGS += $(shell pkg-config --cflags arrow parquet) -DENABLE_ARROW
CORE_SRCS += backend/src/io/parquet_arrow.cc
LIBS += $(shell pkg-config --libs arrow parquet)
endif
endif
endif

# Enforce compiled Parquet by default
ENABLE_ARROW ?= 1

ifeq ($(ENABLE_ARROW),1)
  HAVE_PKGCFG := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)
  # Auto-pick Arrow from vcpkg if present and not explicitly set
  ifeq ($(strip $(ARROW_CFLAGS)),)
    ifneq ($(wildcard $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/include),)
      ARROW_INC_DIR := $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/include
      ARROW_LIB_DIR := $(VCPKG_ROOT)/installed/$(VCPKG_TRIPLET)/lib
      ARROW_CFLAGS := -I$(ARROW_INC_DIR)
      ARROW_LIBS := -L$(ARROW_LIB_DIR) -lparquet -larrow
      # Set rpath for local libs when bundling
      ifeq ($(UNAME_S),Darwin)
        LDFLAGS += -Wl,-rpath,@loader_path
      else ifeq ($(UNAME_S),Linux)
        LDFLAGS += -Wl,-rpath,'$$ORIGIN'
      endif
    endif
  endif
  ifneq ($(strip $(ARROW_CFLAGS)),)
    CPPFLAGS += $(ARROW_CFLAGS) -DENABLE_ARROW
    LIBS += $(ARROW_LIBS)
    CORE_SRCS += backend/src/io/parquet_arrow.cc
  else ifeq ($(HAVE_PKGCFG),1)
    HAVE_ARROW := $(shell pkg-config --exists arrow parquet && echo 1 || echo 0)
    ifeq ($(HAVE_ARROW),1)
      CPPFLAGS += $(shell pkg-config --cflags arrow parquet) -DENABLE_ARROW
      LIBS += $(shell pkg-config --libs arrow parquet)
      CORE_SRCS += backend/src/io/parquet_arrow.cc
    else
      $(warning Apache Arrow/Parquet dev libs not found via pkg-config. Try vcpkg with `make arrow-vcpkg`.)
    endif
  else
    $(warning pkg-config not found. You can set ARROW_CFLAGS/ARROW_LIBS manually or use `make arrow-vcpkg`.)
  endif
else
  # Without Arrow support, compile stub (note: backend will error if Parquet required)
  CORE_SRCS += backend/src/io/parquet_stub.c
endif

RUNNER_OBJ := $(OBJ_DIR)/backend/src/algo/run_entropymax.o
CORE_OBJS  := $(CORE_SRCS:%.c=$(OBJ_DIR)/%.o)

RUNNER_BIN := $(BIN_DIR)/run_entropymax

.PHONY: all runner clean distclean

all: runner

runner: $(CORE_OBJS) $(RUNNER_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $(RUNNER_BIN) $(CORE_OBJS) $(RUNNER_OBJ) $(LDFLAGS) $(LIBS)
	@echo Built $(RUNNER_BIN)

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	@rm -rf $(BUILD_DIR)

distclean: clean
	@echo Clean complete

# -----------------------------------------------------------------------------
# Setup and dependency installation

.PHONY: setup deps arrow-deps pydeps

setup: deps runner

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
	@echo "Windows or unknown OS: compiled Arrow not auto-installed; Python fallback will be used." && true
endif

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
	@cd $(VCPKG_ROOT) && ./bootstrap-vcpkg.sh || ./bootstrap-vcpkg.bat || true

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
	$(VCPKG_ROOT)/vcpkg install arrow[parquet]:$(VCPKG_TRIPLET)
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

# Convenience: full stack setup
setup-all: deps frontend-deps runner


