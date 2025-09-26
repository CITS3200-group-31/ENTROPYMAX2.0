# Cross-platform Makefile for EntropyMax backend
# Supports macOS, Linux, and Windows (MSYS/MinGW) via GCC/Clang

# Detect OS
ifeq ($(OS),Windows_NT)
  OS_NAME := Windows
else
  UNAME_S := $(shell uname -s 2>/dev/null)
  ifeq ($(UNAME_S),Darwin)
    OS_NAME := macOS
  else ifeq ($(UNAME_S),Linux)
    OS_NAME := Linux
  else
    OS_NAME := Unknown
  endif
endif

# Detect architecture (informational)
UNAME_M := $(shell uname -m 2>/dev/null)

# Toolchain and commands
ifeq ($(OS_NAME),Windows)
  CC      ?= gcc
  AR      ?= ar
  EXE_EXT := .exe
  RM      := del /Q
  RMDIR   := rmdir /S /Q
  MKDIR   := mkdir
  DIFF    := fc /N
  SEP     := \\
else
CC      ?= cc
  AR      ?= ar
  EXE_EXT :=
  RM      := rm -f
  RMDIR   := rm -rf
  MKDIR   := mkdir -p
  DIFF    := diff -u
  SEP     := /
endif

# Python
PYTHON := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || command -v python3 || echo python)

# Paths
ROOT_DIR    := $(CURDIR)
BACKEND_DIR := backend
INC_DIR     := $(BACKEND_DIR)/include
ALGO_DIR    := $(BACKEND_DIR)/src/algo
IO_DIR      := $(BACKEND_DIR)/src/io
UTIL_DIR    := $(BACKEND_DIR)/src/util
CLI_DIR     := $(BACKEND_DIR)/src/cli

BUILD_DIR := build-make
OBJ_DIR   := $(BUILD_DIR)/obj
BIN_DIR   := $(BUILD_DIR)/bin
LIB_DIR   := $(BUILD_DIR)/lib

# Flags
CSTD    ?= c11
CPPFLAGS += -I$(INC_DIR) -I$(BACKEND_DIR)/src/algo
CFLAGS   += -std=$(CSTD) -O2 -Wall -Wextra -Wconversion -Wshadow -Wpedantic
LDFLAGS  ?=
LIBS     ?= -lm

ifeq ($(OS_NAME),Windows)
  PICFLAG :=
else
  PICFLAG := -fPIC
endif

CFLAGS += $(PICFLAG)

# Sources
CORE_SRCS := \
  $(ALGO_DIR)/preprocess.c \
  $(ALGO_DIR)/metrics.c \
  $(ALGO_DIR)/grouping.c \
  $(ALGO_DIR)/sweep.c \
  $(UTIL_DIR)/util.c

# Optional io stubs linked into the library for CLI completeness
IO_SRCS := \
  $(IO_DIR)/csv_stub.c \
  $(IO_DIR)/parquet_stub.c \
  $(IO_DIR)/run_converter_execute.c

LIB_SRCS := $(CORE_SRCS) $(IO_SRCS)

RUNNER_SRC := $(ALGO_DIR)/run_entropymax.c
CLI_SRCS   := $(CLI_DIR)/emx_cli.c $(ALGO_DIR)/backend_algo.c

# Objects
LIB_OBJS    := $(patsubst %.c,$(OBJ_DIR)/%.o,$(LIB_SRCS))
RUNNER_OBJ  := $(patsubst %.c,$(OBJ_DIR)/%.o,$(RUNNER_SRC))
CLI_OBJS    := $(patsubst %.c,$(OBJ_DIR)/%.o,$(CLI_SRCS))

# Outputs
STATIC_LIB := $(LIB_DIR)/libentropymax.a
RUNNER_BIN := $(BIN_DIR)/run_entropymax$(EXE_EXT)
CLI_BIN    := $(BIN_DIR)/emx_cli$(EXE_EXT)

.PHONY: all lib runner cli tools verify clean distclean prepare parquet pydeps venv run_parquet

all: pydeps lib runner verify prepare parquet
venv:
	@echo "[venv] Creating local virtualenv if missing"
	@([ -x .venv/bin/python ] || (command -v python3 >/dev/null 2>&1 && python3 -m venv .venv)) || true

pydeps: venv
	@echo "[pydeps] Installing Python dependencies into .venv (pandas, pyarrow)"
	@(.venv/bin/python -m pip install -r $(IO_DIR)/requirements.txt >/dev/null 2>&1 || true)

lib: $(STATIC_LIB)

runner: $(RUNNER_BIN)

tools: $(CLI_BIN)

$(STATIC_LIB): $(LIB_OBJS)
	@$(MKDIR) $(LIB_DIR)
	$(AR) rcs $@ $(LIB_OBJS)

$(RUNNER_BIN): $(STATIC_LIB) $(RUNNER_OBJ) $(PARQUET_OBJ)
	@$(MKDIR) $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(RUNNER_OBJ) $(PARQUET_OBJ) $(STATIC_LIB) $(LDFLAGS) $(LIBS) $(PARQUET_LIBS)

$(CLI_BIN): $(STATIC_LIB) $(CLI_OBJS) $(PARQUET_OBJ)
	@$(MKDIR) $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(CLI_OBJS) $(PARQUET_OBJ) $(STATIC_LIB) $(LDFLAGS) $(LIBS) $(PARQUET_LIBS)

# Pattern rule

$(OBJ_DIR)/%.o: %.c
	@$(MKDIR) $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/%.o: %.cc
	@$(MKDIR) $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

# Verification: regenerate CSV and diff against baseline
verify: pydeps prepare runner
    @echo "[verify] Generating CSV via runner"
    @$(RUNNER_BIN)
    @echo "[verify] Creating expected processed CSV from legacy + GPS"
    $(PYTHON) scripts/convert_legacy_groupings.py --legacy data/raw/legacy_outputs/sample_group_3_output.csv --gps data/raw/gps/sample_group_3_coordinates.csv --out data/processed/sample_output_EXPECTED.csv
    @echo "[verify] Comparing processed frontend CSV vs expected"
    $(PYTHON) scripts/compare_csvs.py data/processed/sample_output_EXPECTED.csv data/processed/sample_output_frontend.csv

# Prepare: merge raw sample CSV and GPS CSV into processed inputs and Parquet
prepare: pydeps
	@echo "[prepare] Merging raw+GPS into processed inputs"
	$(PYTHON) $(IO_DIR)/prepare_input.py data/input.csv data/raw/sample_coordinates.csv

parquet: pydeps verify
	@echo "[parquet] Converting output CSV to Parquet"
	$(PYTHON) $(IO_DIR)/convert_output_to_parquet.py data/processed/sample_outputt.csv data/processed/sample_outputt.parquet

# Run end-to-end from Parquet input to Parquet output
# Usage: make run_parquet IN=data/processed/input_merged.parquet OUT=data/processed/result.parquet
run_parquet: pydeps runner
	@[ -n "$(IN)" ] || (echo "IN not set (path to input merged parquet)" && exit 2)
	@[ -n "$(OUT)" ] || (echo "OUT not set (path to output parquet)" && exit 2)
	$(PYTHON) $(IO_DIR)/run_parquet.py $(IN) $(OUT)

# Parquet/Arrow optional integration
CXX      ?= c++
CXXFLAGS += -O2 -Wall -Wextra -Wpedantic
PARQUET_OBJ :=
# Try pkg-config for arrow/parquet
ARROW_CFLAGS  := $(shell pkg-config --cflags arrow parquet 2>/dev/null)
ARROW_LIBS    := $(shell pkg-config --libs arrow parquet 2>/dev/null)
ifneq ($(ARROW_CFLAGS),)
  CPPFLAGS += $(ARROW_CFLAGS)
  PARQUET_LIBS += $(ARROW_LIBS)
  PARQUET_SRC := $(IO_DIR)/parquet_arrow.cc
  PARQUET_OBJ := $(patsubst %.cc,$(OBJ_DIR)/%.o,$(PARQUET_SRC))
endif

# Prepare: merge raw sample CSV and GPS CSV into processed inputs and Parquet
prepare: pydeps
	@echo "[prepare] Merging raw+GPS into processed inputs"
	$(PYTHON) $(IO_DIR)/prepare_input.py data/input.csv data/raw/sample_coordinates.csv

parquet: pydeps verify
	@echo "[parquet] Converting output CSV to Parquet"
	$(PYTHON) $(IO_DIR)/convert_output_to_parquet.py data/processed/sample_outputt.csv data/processed/sample_outputt.parquet

# Run end-to-end from Parquet input to Parquet output
# Usage: make run_parquet IN=data/processed/input_merged.parquet OUT=data/processed/result.parquet
run_parquet: pydeps runner
	@[ -n "$(IN)" ] || (echo "IN not set (path to input merged parquet)" && exit 2)
	@[ -n "$(OUT)" ] || (echo "OUT not set (path to output parquet)" && exit 2)
	$(PYTHON) $(IO_DIR)/run_parquet.py $(IN) $(OUT)

# Parquet/Arrow optional integration
CXX      ?= c++
CXXFLAGS += -O2 -Wall -Wextra -Wpedantic
PARQUET_OBJ :=
# Try pkg-config for arrow/parquet
ARROW_CFLAGS  := $(shell pkg-config --cflags arrow parquet 2>/dev/null)
ARROW_LIBS    := $(shell pkg-config --libs arrow parquet 2>/dev/null)
ifneq ($(ARROW_CFLAGS),)
  CPPFLAGS += $(ARROW_CFLAGS)
  PARQUET_LIBS += $(ARROW_LIBS)
  PARQUET_SRC := $(IO_DIR)/parquet_arrow.cc
  PARQUET_OBJ := $(patsubst %.cc,$(OBJ_DIR)/%.o,$(PARQUET_SRC))
endif

clean:
	-$(RMDIR) $(BUILD_DIR)

distclean: clean
	@echo "Clean complete"

# Info
print-%:
	@echo '$*=$($*)'


