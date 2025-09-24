cmake_minimum_required(VERSION 3.16)
project(entropymax_backend C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Enable warnings in non-Release builds
if(NOT CMAKE_BUILD_TYPE STREQUAL "Release")
  add_compile_options(-Wall -Wextra -Wconversion -Wshadow -Wpedantic)
endif()

# Optional sanitizers for dev builds (enable by setting -DSANITIZE=ON)
option(SANITIZE "Enable Address/UB sanitizers" OFF)
if(SANITIZE AND NOT CMAKE_BUILD_TYPE STREQUAL "Release")
  add_compile_options(-fsanitize=address,undefined)
  add_link_options(-fsanitize=address,undefined)
endif()

add_library(entropymax STATIC
  src/algo/preprocess.c
  src/algo/metrics.c
  src/algo/grouping.c
  src/algo/sweep.c
  src/io/run_converter_execute.c
  src/io/csv_stub.c
  src/io/parquet_stub.c
  src/util/util.c
)
target_include_directories(entropymax PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

option(BUILD_TOOLS "Build CLI/tools" ON)
if(BUILD_TOOLS)
  add_executable(emx_cli src/cli/emx_cli.c src/algo/backend_algo.c)
  target_link_libraries(emx_cli PRIVATE entropymax)
  add_executable(run_entropymax src/algo/run_entropymax.c src/algo/preprocess.c src/algo/metrics.c src/algo/grouping.c src/algo/sweep.c src/util/util.c)
  target_include_directories(run_entropymax PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
endif()

enable_testing()
add_executable(test_backend tests/test_backend.c)
target_link_libraries(test_backend PRIVATE entropymax)
add_test(NAME backend_tests COMMAND test_backend)

# Verification test: regenerate CSV and diff against baseline
add_custom_target(verify_csv
  COMMAND ${CMAKE_COMMAND} -E env "PWD=${CMAKE_BINARY_DIR}"
          ${CMAKE_COMMAND} -E echo "Running developer runner and diffing CSV"
  COMMAND ${CMAKE_COMMAND} -E env ${CMAKE_CURRENT_SOURCE_DIR}/../.. ./run_entropymax
  COMMAND ${CMAKE_COMMAND} -E compare_files
          ${CMAKE_CURRENT_SOURCE_DIR}/../data/processed/sample_outputt.csv
          ${CMAKE_CURRENT_SOURCE_DIR}/../data/processed/sample_output_CORRECT.csv
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/..
)

add_test(NAME verify_csv_diff
  COMMAND ${CMAKE_COMMAND} -E compare_files
          ${CMAKE_SOURCE_DIR}/../data/processed/sample_outputt.csv
          ${CMAKE_SOURCE_DIR}/../data/processed/sample_output_CORRECT.csv)

