Parquet I/O
===========

This backend supports two modes:

1) Compiled Arrow/Parquet (recommended)
   - Build with -DENABLE_ARROW and link Arrow/Parquet.
   - Provides em_csv_to_parquet_with_gps (C++) and parquet_is_available()=1.
   - Runner writes Parquet directly from the algorithm CSV.

2) Stub mode (default in repo)
   - parquet_stub.c returns parquet_is_available()=0 and no-ops.
   - Runner falls back to Python converter (scripts/convert_output_to_parquet.py).

To enable Arrow:
  - Install Apache Arrow C++ and Parquet development libs
  - Update Makefile to compile with -DENABLE_ARROW and link arrow/parquet


