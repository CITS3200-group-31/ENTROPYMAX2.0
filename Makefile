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
	backend/src/io/csv_stub.c \
	backend/src/io/parquet_stub.c

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


