#include <arrow/api.h>
#include <arrow/status.h>
#include <arrow/result.h>
#include <arrow/io/api.h>
#include <parquet/arrow/writer.h>
#include <parquet/arrow/reader.h>
#include <arrow/csv/api.h>
#include <unordered_map>
#include <memory>
#include <string>
#include <vector>

// Minimal compiled postprocess: write output parquet given CSV-like columns in memory.
// Expose simple C-linkage wrappers as needed from C code.

extern "C" {

// Writes a parquet file from arrays of UTF-8 columns, where the first N-2
// columns come from the legacy CSV and the last two are latitude/longitude doubles.
// Inputs:
//  - csv_strings: vector of string columns (size string_cols)
//  - string_cols: number of string columns
//  - lat: pointer to latitude values (rows)
//  - lon: pointer to longitude values (rows)
//  - rows: number of rows
//  - out_path: parquet output path
// Returns 0 on success, non-zero on failure.
int em_write_parquet_with_latlon(
  const char *out_path,
  const char *const *const *csv_strings, // csv_strings[col][row] C strings
  int32_t string_cols,
  const double *lat,
  const double *lon,
  int32_t rows)
{
  try {
    arrow::MemoryPool *pool = arrow::default_memory_pool();

    std::vector<std::shared_ptr<arrow::Array>> arrays;
    std::vector<std::shared_ptr<arrow::Field>> fields;

    // Build string columns
    for (int32_t c = 0; c < string_cols; ++c) {
      arrow::StringBuilder sb(pool);
      for (int32_t r = 0; r < rows; ++r) {
        const char *s = csv_strings[c][r];
        if (!s) s = "";
        if (!sb.Append(s).ok()) return 2;
      }
      std::shared_ptr<arrow::Array> arr;
      if (!sb.Finish(&arr).ok()) return 3;
      arrays.push_back(arr);
      fields.push_back(arrow::field(std::string("col") + std::to_string(c), arrow::utf8()));
    }

    // Latitude/Longitude as double arrays
    {
      arrow::DoubleBuilder db(pool);
      for (int32_t r = 0; r < rows; ++r) { if (!db.Append(lat[r]).ok()) return 4; }
      std::shared_ptr<arrow::Array> arr; if (!db.Finish(&arr).ok()) return 5;
      arrays.push_back(arr);
      fields.push_back(arrow::field("latitude", arrow::float64()));
    }
    {
      arrow::DoubleBuilder db(pool);
      for (int32_t r = 0; r < rows; ++r) { if (!db.Append(lon[r]).ok()) return 6; }
      std::shared_ptr<arrow::Array> arr; if (!db.Finish(&arr).ok()) return 7;
      arrays.push_back(arr);
      fields.push_back(arrow::field("longitude", arrow::float64()));
    }

    auto schema = std::make_shared<arrow::Schema>(fields);
    auto table = arrow::Table::Make(schema, arrays, rows);
    auto sink_res = arrow::io::FileOutputStream::Open(out_path);
    if (!sink_res.ok()) return 8;
    std::shared_ptr<arrow::io::OutputStream> sink = std::static_pointer_cast<arrow::io::OutputStream>(*sink_res);
    auto wst = parquet::arrow::WriteTable(*table, pool, sink, 1024);
    if (!wst.ok()) return 9;
    return 0;
  } catch (...) {
    return 99;
  }
}

// Compiled-only helper: read algorithm CSV and GPS CSV, append lat/lon, write Parquet.
// Returns 0 on success.
int em_csv_to_parquet_with_gps(
  const char *algo_csv_path,
  const char *gps_csv_path,
  const char *out_parquet_path)
{
  try {
    arrow::MemoryPool *pool = arrow::default_memory_pool();

    // Read algorithm CSV (header present)
    auto read_opts = arrow::csv::ReadOptions::Defaults();
    read_opts.autogenerate_column_names = false;
    auto parse_opts = arrow::csv::ParseOptions::Defaults();
    auto convert_opts = arrow::csv::ConvertOptions::Defaults();
    arrow::io::IOContext io_ctx(pool);

    auto algo_in_res = arrow::io::ReadableFile::Open(algo_csv_path);
    if (!algo_in_res.ok()) return 20;
    auto algo_reader_res = arrow::csv::TableReader::Make(io_ctx, *algo_in_res, read_opts, parse_opts, convert_opts);
    if (!algo_reader_res.ok()) return 21;
    auto algo_table_res = (*algo_reader_res)->Read();
    if (!algo_table_res.ok()) return 22;
    std::shared_ptr<arrow::Table> algo_table = *algo_table_res;

    // Read GPS CSV (header present)
    auto gps_in_res = arrow::io::ReadableFile::Open(gps_csv_path);
    if (!gps_in_res.ok()) return 23;
    auto gps_reader_res = arrow::csv::TableReader::Make(io_ctx, *gps_in_res, read_opts, parse_opts, convert_opts);
    if (!gps_reader_res.ok()) return 24;
    auto gps_table_res = (*gps_reader_res)->Read();
    if (!gps_table_res.ok()) return 25;
    std::shared_ptr<arrow::Table> gps_table = *gps_table_res;

    // Normalize GPS column names: accept "Sample" or "Sample Name"
    auto gps_schema = gps_table->schema();
    int sample_idx_gps = gps_schema->GetFieldIndex("Sample");
    if (sample_idx_gps < 0) sample_idx_gps = gps_schema->GetFieldIndex("Sample Name");
    int lat_idx = gps_schema->GetFieldIndex("Latitude");
    int lon_idx = gps_schema->GetFieldIndex("Longitude");
    if (sample_idx_gps < 0 || lat_idx < 0 || lon_idx < 0) return 10;

    // Build sample -> (lat,lon) map, dedup by first seen
    std::unordered_map<std::string, std::pair<double,double>> gps_map;
    auto gps_sample = std::static_pointer_cast<arrow::StringArray>(gps_table->column(sample_idx_gps)->chunk(0));
    auto gps_lat = std::static_pointer_cast<arrow::DoubleArray>(gps_table->column(lat_idx)->chunk(0));
    auto gps_lon = std::static_pointer_cast<arrow::DoubleArray>(gps_table->column(lon_idx)->chunk(0));
    int64_t gps_rows = gps_table->num_rows();
    for (int64_t i = 0; i < gps_rows; ++i) {
      if (gps_sample->IsNull(i) || gps_lat->IsNull(i) || gps_lon->IsNull(i)) continue;
      std::string s = gps_sample->GetString(i);
      // trim
      while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
      size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
      if (gps_map.find(s) == gps_map.end()) {
        gps_map.emplace(std::move(s), std::make_pair(gps_lat->Value(i), gps_lon->Value(i)));
      }
    }

    // Extract algorithm Sample and K columns
    auto algo_schema = algo_table->schema();
    int idx_group = algo_schema->GetFieldIndex("Group");
    int idx_sample = algo_schema->GetFieldIndex("Sample");
    int idx_k = algo_schema->GetFieldIndex("K");
    if (idx_group < 0 || idx_sample < 0 || idx_k < 0) return 41; // output CSV should have 'Sample' header

    // Find metrics start by locating the known first metric "% explained"
    int idx_metrics_start = algo_schema->GetFieldIndex("% explained");
    if (idx_metrics_start < 0) return 43; // require K present in CSV output

    // Build lat/lon arrays aligned to algorithm rows
    auto algo_sample_arr = std::static_pointer_cast<arrow::StringArray>(algo_table->column(idx_sample)->chunk(0));
    int64_t rows = algo_table->num_rows();
    arrow::DoubleBuilder lat_b(pool), lon_b(pool);
    for (int64_t i = 0; i < rows; ++i) {
      std::string s = algo_sample_arr->IsNull(i) ? std::string() : algo_sample_arr->GetString(i);
      while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
      size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
      auto it = gps_map.find(s);
      if (it == gps_map.end()) {
        auto st1 = lat_b.AppendNull(); if (!st1.ok()) return 26;
        auto st2 = lon_b.AppendNull(); if (!st2.ok()) return 27;
      } else {
        auto st1 = lat_b.Append(it->second.first); if (!st1.ok()) return 28;
        auto st2 = lon_b.Append(it->second.second); if (!st2.ok()) return 29;
      }
    }
    std::shared_ptr<arrow::Array> lat_arr, lon_arr;
    if (!lat_b.Finish(&lat_arr).ok()) return 30;
    if (!lon_b.Finish(&lon_arr).ok()) return 31;

    // Reconstruct table in frontend-required order:
    // [Group, Sample, bins..., metrics..., K, latitude, longitude]
    std::vector<std::shared_ptr<arrow::ChunkedArray>> cols;
    std::vector<std::shared_ptr<arrow::Field>> fields;

    cols.push_back(algo_table->column(idx_group));
    fields.push_back(algo_schema->field(idx_group));
    cols.push_back(algo_table->column(idx_sample));
    fields.push_back(algo_schema->field(idx_sample));

    // Bins: from (idx_sample+1) up to (idx_metrics_start-1)
    for (int i = idx_sample + 1; i < idx_metrics_start; ++i) {
      cols.push_back(algo_table->column(i));
      fields.push_back(algo_schema->field(i));
    }
    // Metrics: from idx_metrics_start up to (excluding) idx_k? In CSV, K was before Group and metrics after bins.
    // However, we rely on explicit K at end, so include all columns except K among the remaining.
    int nfields = static_cast<int>(algo_schema->num_fields());
    for (int i = idx_metrics_start; i < nfields; ++i) {
      if (i == idx_k) continue; // skip original K; we'll append at the end
      cols.push_back(algo_table->column(i));
      fields.push_back(algo_schema->field(i));
    }
    // Append K third-from-last
    cols.push_back(algo_table->column(idx_k));
    fields.push_back(algo_schema->field(idx_k));

    // Append latitude, longitude
    auto lat_chunked = std::make_shared<arrow::ChunkedArray>(lat_arr);
    cols.push_back(lat_chunked);
    fields.push_back(arrow::field("latitude", arrow::float64()));
    auto lon_chunked = std::make_shared<arrow::ChunkedArray>(lon_arr);
    cols.push_back(lon_chunked);
    fields.push_back(arrow::field("longitude", arrow::float64()));

    auto final_schema = std::make_shared<arrow::Schema>(fields);
    auto final_tbl = arrow::Table::Make(final_schema, cols);

    // Write Parquet
    auto sink_res2 = arrow::io::FileOutputStream::Open(out_parquet_path);
    if (!sink_res2.ok()) return 34;
    std::shared_ptr<arrow::io::OutputStream> sink = std::static_pointer_cast<arrow::io::OutputStream>(*sink_res2);
    auto st = parquet::arrow::WriteTable(*final_tbl, pool, sink, 1024);
    if (!st.ok()) return 12;
    return 0;
  } catch (...) {
    return 99;
  }
}

}


