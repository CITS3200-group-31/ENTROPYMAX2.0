SHELL := /bin/bash

.PHONY: all clean

all:
	cmake -S backend -B backend/build-msvc
	cmake --build backend/build-msvc --config Release --target run_entropymax

clean:
	rm -rf backend/build-msvc build/bin build/dlls


