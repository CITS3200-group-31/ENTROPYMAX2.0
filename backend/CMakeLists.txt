cmake_minimum_required(VERSION 3.16)
project(entropymax_backend C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(entropymax STATIC
  src/algo/backend_algo.c
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

add_executable(emx_cli src/cli/emx_cli.c)
target_link_libraries(emx_cli PRIVATE entropymax)

enable_testing()
add_executable(test_backend tests/test_backend.c)
target_link_libraries(test_backend PRIVATE entropymax)
add_test(NAME backend_tests COMMAND test_backend)

