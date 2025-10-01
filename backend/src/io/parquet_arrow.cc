#ifdef ENABLE_ARROW
#include "parquet.h"

#include <arrow/api.h>
#include <arrow/csv/api.h>
#include <arrow/io/api.h>
#include <parquet/arrow/writer.h>
#include <parquet/arrow/reader.h>

#include <memory>
#include <string>
#include <fstream>

extern "C" {
int em_csv_to_parquet_with_gps(const char *algo_csv_path,
                               const char *gps_csv_path,
                               const char *out_parquet_path);
// New helper: write both Parquet and processed CSV (frontend order) without filtering to optimal K
int em_csv_to_both_with_gps(const char *algo_csv_path,
                            const char *gps_csv_path,
                            const char *out_parquet_path,
                            const char *out_csv_path);
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

int em_csv_to_both_with_gps(const char *algo_csv_path,
                            const char *gps_csv_path,
                            const char *out_parquet_path,
                            const char *out_csv_path) {
  using arrow::Status;
  using arrow::Table;
  if (!algo_csv_path || !gps_csv_path || !out_parquet_path || !out_csv_path) return -1;

  // Read algorithm CSV
  std::shared_ptr<Table> algo_table;
  if (!ReadCsvToTable(algo_csv_path, &algo_table).ok()) return -2;

  // Read GPS CSV
  std::shared_ptr<Table> gps_table;
  if (!ReadCsvToTable(gps_csv_path, &gps_table).ok()) return -3;

  // Build Sample -> (lat,lon) map; accept "Sample" or "Sample Name"
  auto gps_schema = gps_table->schema();
  int sample_idx_gps = gps_schema->GetFieldIndex("Sample");
  if (sample_idx_gps < 0) sample_idx_gps = gps_schema->GetFieldIndex("Sample Name");
  int lat_idx = gps_schema->GetFieldIndex("Latitude");
  int lon_idx = gps_schema->GetFieldIndex("Longitude");
  if (sample_idx_gps < 0 || lat_idx < 0 || lon_idx < 0) return -4;

  std::unordered_map<std::string, std::pair<double,double>> gps_map;
  auto gps_sample = std::static_pointer_cast<arrow::StringArray>(gps_table->column(sample_idx_gps)->chunk(0));
  auto gps_lat = std::static_pointer_cast<arrow::DoubleArray>(gps_table->column(lat_idx)->chunk(0));
  auto gps_lon = std::static_pointer_cast<arrow::DoubleArray>(gps_table->column(lon_idx)->chunk(0));
  int64_t gps_rows = gps_table->num_rows();
  for (int64_t i = 0; i < gps_rows; ++i) {
    if (gps_sample->IsNull(i) || gps_lat->IsNull(i) || gps_lon->IsNull(i)) continue;
    std::string s = gps_sample->GetString(i);
    while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
    size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
    if (gps_map.find(s) == gps_map.end()) {
      gps_map.emplace(std::move(s), std::make_pair(gps_lat->Value(i), gps_lon->Value(i)));
    }
  }

  // Locate columns in algo CSV
  auto algo_schema = algo_table->schema();
  int idx_group = algo_schema->GetFieldIndex("Group");
  int idx_sample = algo_schema->GetFieldIndex("Sample");
  int idx_k = algo_schema->GetFieldIndex("K");
  int idx_metrics_start = algo_schema->GetFieldIndex("% explained");
  if (idx_group < 0 || idx_sample < 0 || idx_k < 0 || idx_metrics_start < 0) return -5;

  // Build lat/lon arrays aligned with algo rows
  auto algo_sample_arr = std::static_pointer_cast<arrow::StringArray>(algo_table->column(idx_sample)->chunk(0));
  int64_t rows = algo_table->num_rows();
  arrow::DoubleBuilder lat_b, lon_b;
  for (int64_t i = 0; i < rows; ++i) {
    std::string s = algo_sample_arr->IsNull(i) ? std::string() : algo_sample_arr->GetString(i);
    while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
    size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
    auto it = gps_map.find(s);
    if (it == gps_map.end()) { ARROW_UNUSED(lat_b.AppendNull()); ARROW_UNUSED(lon_b.AppendNull()); }
    else { ARROW_UNUSED(lat_b.Append(it->second.first)); ARROW_UNUSED(lon_b.Append(it->second.second)); }
  }
  std::shared_ptr<arrow::Array> lat_arr, lon_arr;
  if (!lat_b.Finish(&lat_arr).ok()) return -6;
  if (!lon_b.Finish(&lon_arr).ok()) return -7;

  // Reconstruct table in frontend-required order: [Group, Sample, bins..., metrics..., K, latitude, longitude]
  std::vector<std::shared_ptr<arrow::ChunkedArray>> cols;
  std::vector<std::shared_ptr<arrow::Field>> fields;
  cols.push_back(algo_table->column(idx_group)); fields.push_back(algo_schema->field(idx_group));
  cols.push_back(algo_table->column(idx_sample)); fields.push_back(algo_schema->field(idx_sample));
  // Bins
  for (int i = idx_sample + 1; i < idx_metrics_start; ++i) {
    cols.push_back(algo_table->column(i));
    fields.push_back(algo_schema->field(i));
  }
  // Metrics (skip original K)
  int nfields = static_cast<int>(algo_schema->num_fields());
  for (int i = idx_metrics_start; i < nfields; ++i) {
    if (i == idx_k) continue;
    cols.push_back(algo_table->column(i));
    fields.push_back(algo_schema->field(i));
  }
  // Ensure leading bin "0.02" exists; if not, insert a zero column after Sample
  if (algo_schema->GetFieldIndex("0.02") < 0) {
    arrow::DoubleBuilder zero_b;
    ARROW_UNUSED(zero_b.Reserve(rows));
    for (int64_t r = 0; r < rows; ++r) ARROW_UNUSED(zero_b.Append(0.0));
    std::shared_ptr<arrow::Array> zero_arr;
    if (zero_b.Finish(&zero_arr).ok()) {
      auto zero_chunked = std::make_shared<arrow::ChunkedArray>(zero_arr);
      cols.insert(cols.begin() + 2, zero_chunked);
      fields.insert(fields.begin() + 2, arrow::field("0.02", arrow::float64()));
    }
  }
  // Append K, latitude, longitude
  cols.push_back(algo_table->column(idx_k)); fields.push_back(algo_schema->field(idx_k));
  cols.push_back(std::make_shared<arrow::ChunkedArray>(lat_arr)); fields.push_back(arrow::field("latitude", arrow::float64()));
  cols.push_back(std::make_shared<arrow::ChunkedArray>(lon_arr)); fields.push_back(arrow::field("longitude", arrow::float64()));

  auto final_schema = std::make_shared<arrow::Schema>(fields);
  auto final_tbl = arrow::Table::Make(final_schema, cols);

  // Write Parquet
  {
    auto open_res = arrow::io::FileOutputStream::Open(out_parquet_path);
    if (!open_res.ok()) return -8;
    auto sink = *open_res;
    auto st = parquet::arrow::WriteTable(*final_tbl, arrow::default_memory_pool(), sink, 1024);
    if (!st.ok()) return -9;
  }

  // Write CSV
  {
    std::ofstream ofs(out_csv_path, std::ios::out | std::ios::trunc);
    if (!ofs.is_open()) return -10;
    // Header
    for (int i = 0; i < final_schema->num_fields(); ++i) { if (i) ofs << ","; ofs << final_schema->field(i)->name(); }
    ofs << "\n";
    int num_cols = static_cast<int>(final_tbl->num_columns());
    int64_t num_rows = final_tbl->num_rows();
    std::vector<std::shared_ptr<arrow::Array>> arrs; arrs.reserve(num_cols);
    for (int c = 0; c < num_cols; ++c) arrs.push_back(final_tbl->column(c)->chunk(0));
    for (int64_t r = 0; r < num_rows; ++r) {
      for (int c = 0; c < num_cols; ++c) {
        if (c) ofs << ",";
        auto arr = arrs[c];
        switch (arr->type_id()) {
          case arrow::Type::STRING: {
            auto sa = std::static_pointer_cast<arrow::StringArray>(arr);
            if (!sa->IsNull(r)) ofs << sa->GetString(r);
            break;
          }
          case arrow::Type::DOUBLE: {
            auto da = std::static_pointer_cast<arrow::DoubleArray>(arr);
            if (!da->IsNull(r)) ofs << da->Value(r);
            break;
          }
          case arrow::Type::INT64: {
            auto ia = std::static_pointer_cast<arrow::Int64Array>(arr);
            if (!ia->IsNull(r)) ofs << ia->Value(r);
            break;
          }
          default: break;
        }
      }
      ofs << "\n";
    }
    ofs.close();
  }

  return 0;
}

#else
// Fallback when Arrow is not enabled
#include "parquet.h"
int parquet_is_available(void) { return 0; }
int parquet_write_table(const char*, const double*, int32_t, int32_t, const char* const*, const char* const*) { return -1; }
int em_csv_to_parquet_with_gps(const char*, const char*, const char*) { return -1; }
int em_csv_to_both_with_gps(const char*, const char*, const char*, const char*) { return -1; }
#endif


