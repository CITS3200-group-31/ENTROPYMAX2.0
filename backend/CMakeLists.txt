cmake_minimum_required(VERSION 3.16)
project(entropymax_backend C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

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

  # Optional Arrow/Parquet integration for compiled-only IO
  find_package(Arrow CONFIG QUIET)
  if(Arrow_FOUND)
    message(STATUS "Arrow found: enabling compiled Parquet writer")
    target_compile_definitions(entropymax PRIVATE EM_HAVE_ARROW)

    set(EM_ARROW_LINK_TARGETS)
    if(TARGET Arrow::arrow)
      list(APPEND EM_ARROW_LINK_TARGETS Arrow::arrow)
    endif()
    if(TARGET Parquet::parquet)
      list(APPEND EM_ARROW_LINK_TARGETS Parquet::parquet)
    endif()

    add_library(parquet_io STATIC src/io/parquet_io.cc)
    target_include_directories(parquet_io PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

    if(EM_ARROW_LINK_TARGETS)
      target_link_libraries(parquet_io PUBLIC ${EM_ARROW_LINK_TARGETS})
    else()
      if(DEFINED Arrow_LIBRARIES)
        target_link_libraries(parquet_io PUBLIC ${Arrow_LIBRARIES})
      else()
        find_library(ARROW_LIB NAMES arrow arrow_static arrow_shared)
        find_library(PARQUET_LIB NAMES parquet parquet_static parquet_shared)
        if(ARROW_LIB AND PARQUET_LIB)
          target_link_libraries(parquet_io PUBLIC ${ARROW_LIB} ${PARQUET_LIB})
        else()
          message(FATAL_ERROR "Arrow libs not found for fallback linking")
        endif()
      endif()
      if(DEFINED Arrow_INCLUDE_DIRS)
        target_include_directories(parquet_io PUBLIC ${Arrow_INCLUDE_DIRS})
      else()
        find_path(ARROW_INCLUDE_DIR NAMES arrow/api.h)
        if(ARROW_INCLUDE_DIR)
          target_include_directories(parquet_io PUBLIC ${ARROW_INCLUDE_DIR})
        endif()
      endif()
    endif()

    add_executable(run_entropymax src/algo/run_entropymax.c src/algo/preprocess.c src/algo/metrics.c src/algo/grouping.c src/algo/sweep.c src/util/util.c)
    target_include_directories(run_entropymax PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(run_entropymax PRIVATE entropymax parquet_io)

    # Parquet verification tool
    add_executable(verify_parquet tests/verify_parquet.cc)
    target_link_libraries(verify_parquet PRIVATE parquet_io)
    add_test(NAME verify_parquet_schema COMMAND verify_parquet)
  else()
    message(WARNING "Arrow not found; building run_entropymax without compiled Parquet writer")
    add_executable(run_entropymax src/algo/run_entropymax.c src/algo/preprocess.c src/algo/metrics.c src/algo/grouping.c src/algo/sweep.c src/util/util.c)
    target_include_directories(run_entropymax PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(run_entropymax PRIVATE entropymax)
  endif()
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

