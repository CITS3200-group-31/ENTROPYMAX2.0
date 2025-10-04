cmake_minimum_required(VERSION 3.16)
project(entropymax_backend C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Consolidate all build outputs (exe/lib) to top-level build/bin
set(EMX_TOP_BIN "${CMAKE_CURRENT_SOURCE_DIR}/../build/bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${EMX_TOP_BIN}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${EMX_TOP_BIN}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${EMX_TOP_BIN}")
foreach(OUTPUTCONFIG DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
  string(TOUPPER "${OUTPUTCONFIG}" OUTPUTCONFIG_UPPER)
  set("CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER}" "${EMX_TOP_BIN}")
  set("CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER}" "${EMX_TOP_BIN}")
  set("CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER}" "${EMX_TOP_BIN}")
endforeach()

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
  src/io/csv_stub.c
  src/io/parquet_stub.c
  src/util/util.c
)
target_include_directories(entropymax PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

option(BUILD_TOOLS "Build CLI/tools" ON)
if(BUILD_TOOLS)
  add_executable(emx_cli src/algo/cli/emx_cli.c src/algo/backend_algo.c)
  target_link_libraries(emx_cli PRIVATE entropymax)

  # Optional Arrow/Parquet integration for compiled-only IO
  find_package(Arrow CONFIG QUIET)
  if(Arrow_FOUND)
    message(STATUS "Arrow found: enabling compiled Parquet writer")
    add_library(parquet_io STATIC src/io/parquet_arrow.cc)
    target_include_directories(parquet_io PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_compile_definitions(parquet_io PUBLIC ENABLE_ARROW)

    # Prefer CMake targets if present
    if(TARGET Arrow::arrow)
      target_link_libraries(parquet_io PUBLIC Arrow::arrow)
    endif()
    if(TARGET Arrow::parquet)
      target_link_libraries(parquet_io PUBLIC Arrow::parquet)
    endif()
    if(TARGET Arrow::csv)
      target_link_libraries(parquet_io PUBLIC Arrow::csv)
    endif()

    # Fallback for environments where imported targets are not provided
    if(NOT TARGET Arrow::arrow OR NOT TARGET Arrow::parquet)
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
  endif()

  add_executable(run_entropymax
    src/algo/run_entropymax.c
    src/algo/preprocess.c
    src/algo/metrics.c
    src/algo/grouping.c
    src/algo/sweep.c
    src/util/util.c)
  target_include_directories(run_entropymax PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
  # Link parquet_io when Arrow is available; always link core library
  if(Arrow_FOUND)
    # Ensure Arrow implementation of parquet_is_available() is preferred over stub
    target_link_libraries(run_entropymax PRIVATE parquet_io)
  endif()
  target_link_libraries(run_entropymax PRIVATE entropymax)

  # Centralize runtime DLLs under top-level build/dlls for distribution and PATH-based loading
  if(WIN32 AND Arrow_FOUND)
    # Known runtime DLLs required by Arrow/Parquet on Windows (vcpkg triplet x64-windows)
    set(EMX_DLL_NAMES
      arrow.dll
      parquet.dll
      brotlicommon.dll
      brotlidec.dll
      brotlienc.dll
      bz2.dll
      lz4.dll
      snappy.dll
      zlib1.dll
      zstd.dll
      libcrypto-3-x64.dll
      utf8proc.dll
      re2.dll
      abseil_dll.dll
      gflags.dll
      libssl-3-x64.dll
      event.dll
      event_core.dll
      event_extra.dll
    )
    set(EMX_VCPKG_BIN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../third_party/vcpkg/installed/x64-windows/bin")
    set(EMX_DLLS_OUT_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/../build/dlls")
    add_custom_command(TARGET run_entropymax POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E make_directory "${EMX_DLLS_OUT_DIR}")
    foreach(dll ${EMX_DLL_NAMES})
      add_custom_command(TARGET run_entropymax POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${EMX_VCPKG_BIN_DIR}/${dll}"
                "${EMX_DLLS_OUT_DIR}/${dll}")
    endforeach()
  endif()

  # Parquet verification disabled in CSV-only mode
  # Also stage executable to top-level build/bin for convenience
  set(EMX_STAGE_BIN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../build/bin")
  add_custom_command(TARGET run_entropymax POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${EMX_STAGE_BIN_DIR}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE:run_entropymax>"
            "${EMX_STAGE_BIN_DIR}/run_entropymax.exe")
endif()

enable_testing()
add_executable(test_backend tests/test_backend.c)
target_link_libraries(test_backend PRIVATE entropymax)
add_test(NAME backend_tests COMMAND test_backend)

