#ifdef ENABLE_ARROW
#include "parquet.h"

#include <arrow/api.h>
#include <arrow/csv/api.h>
#include <arrow/io/api.h>
#include <parquet/arrow/writer.h>

#include <memory>
#include <string>

extern "C" {
int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path);
}

static arrow::Status ReadCsvToTable(const std::string &csv_path,
                                    std::shared_ptr<arrow::Table> *out) {
  ARROW_ASSIGN_OR_RAISE(auto infile, arrow::io::ReadableFile::Open(csv_path));
  auto read_options = arrow::csv::ReadOptions::Defaults();
  read_options.autogenerate_column_names = false;
  auto parse_options = arrow::csv::ParseOptions::Defaults();
  auto convert_options = arrow::csv::ConvertOptions::Defaults();
  ARROW_ASSIGN_OR_RAISE(
      auto reader,
      arrow::csv::TableReader::Make(arrow::io::default_io_context(), infile,
                                    read_options, parse_options, convert_options));
  ARROW_ASSIGN_OR_RAISE(auto table, reader->Read());
  *out = table;
  return arrow::Status::OK();
}

extern "C" int parquet_is_available(void) { return 1; }

extern "C" int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols,
                        const char *const *colnames, const char *const *rownames) {
  (void)data; (void)rows; (void)cols; (void)colnames; (void)rownames; (void)path;
  // Not used in current flow; CSV->Parquet path is used instead.
  return -1;
}

int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path) {
  (void)gps_csv_path; // CSV already contains latitude/longitude columns at the end
  std::shared_ptr<arrow::Table> table;
  auto st = ReadCsvToTable(algo_csv_path, &table);
  if (!st.ok()) {
    return -1;
  }
  std::shared_ptr<arrow::io::FileOutputStream> outfile;
  auto res = arrow::io::FileOutputStream::Open(out_parquet_path);
  if (!res.ok()) return -2;
  outfile = *res;
  parquet::WriterProperties::Builder builder;
  auto props = builder.build();
  auto status = parquet::arrow::WriteTable(*table, arrow::default_memory_pool(), outfile, /*chunk_size=*/65536, props);
  if (!status.ok()) {
    return -3;
  }
  return 0;
}

#else
// Fallback when Arrow is not enabled
#include "parquet.h"
int parquet_is_available(void) { return 0; }
int parquet_write_table(const char*, const double*, int32_t, int32_t, const char* const*, const char* const*) { return -1; }
int em_csv_to_parquet_with_gps(const char*, const char*, const char*) { return -1; }
#endif


