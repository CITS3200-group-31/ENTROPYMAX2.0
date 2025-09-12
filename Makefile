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

.PHONY: all lib runner cli tools verify clean distclean

all: lib runner verify

lib: $(STATIC_LIB)

runner: $(RUNNER_BIN)

tools: $(CLI_BIN)

$(STATIC_LIB): $(LIB_OBJS)
	@$(MKDIR) $(LIB_DIR)
	$(AR) rcs $@ $(LIB_OBJS)

$(RUNNER_BIN): $(STATIC_LIB) $(RUNNER_OBJ)
	@$(MKDIR) $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $(RUNNER_OBJ) $(STATIC_LIB) $(LDFLAGS) $(LIBS)

$(CLI_BIN): $(STATIC_LIB) $(CLI_OBJS)
	@$(MKDIR) $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $(CLI_OBJS) $(STATIC_LIB) $(LDFLAGS) $(LIBS)

# Pattern rule
$(OBJ_DIR)/%.o: %.c
	@$(MKDIR) $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# Verification: regenerate CSV and diff against baseline
verify: runner
	@echo "[verify] Generating CSV via runner"
	@$(RUNNER_BIN)
	@echo "[verify] Comparing against baseline"
ifeq ($(OS_NAME),Windows)
	@$(DIFF) data\processed\sample_output_CORRECT.csv data\processed\sample_outputt.csv
else
	@$(DIFF) data/processed/sample_output_CORRECT.csv data/processed/sample_outputt.csv
endif
	@echo "[verify] Baseline match OK"

clean:
	-$(RMDIR) $(BUILD_DIR)

distclean: clean
	@echo "Clean complete"

# Info
print-%:
	@echo '$*=$($*)'


