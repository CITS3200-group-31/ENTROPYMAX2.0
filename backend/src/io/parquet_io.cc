#include <arrow/api.h>
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
    std::shared_ptr<arrow::io::FileOutputStream> sink;
    auto sink_res = arrow::io::FileOutputStream::Open(out_path);
    if (!sink_res.ok()) return 8;
    sink = *sink_res;
    if (!parquet::arrow::WriteTable(*table, pool, sink, 1024).ok()) return 9;
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
    auto pool = arrow::default_memory_pool();

    // Read algorithm CSV (header present)
    ARROW_ASSIGN_OR_RAISE(auto algo_in, arrow::io::ReadableFile::Open(algo_csv_path));
    auto read_opts = arrow::csv::ReadOptions::Defaults();
    read_opts.autogenerate_column_names = false;
    auto parse_opts = arrow::csv::ParseOptions::Defaults();
    auto convert_opts = arrow::csv::ConvertOptions::Defaults();
    ARROW_ASSIGN_OR_RAISE(auto algo_reader,
      arrow::csv::TableReader::Make(pool, algo_in, read_opts, parse_opts, convert_opts));
    ARROW_ASSIGN_OR_RAISE(auto algo_table, algo_reader->Read());

    // Read GPS CSV (header present)
    ARROW_ASSIGN_OR_RAISE(auto gps_in, arrow::io::ReadableFile::Open(gps_csv_path));
    ARROW_ASSIGN_OR_RAISE(auto gps_reader,
      arrow::csv::TableReader::Make(pool, gps_in, read_opts, parse_opts, convert_opts));
    ARROW_ASSIGN_OR_RAISE(auto gps_table, gps_reader->Read());

    // Normalize GPS column names: accept "Sample" or "Sample Name"
    auto gps_schema = gps_table->schema();
    int sample_idx = gps_schema->GetFieldIndex("Sample");
    if (sample_idx < 0) sample_idx = gps_schema->GetFieldIndex("Sample Name");
    int lat_idx = gps_schema->GetFieldIndex("Latitude");
    int lon_idx = gps_schema->GetFieldIndex("Longitude");
    if (sample_idx < 0 || lat_idx < 0 || lon_idx < 0) return 10;

    // Build sample -> (lat,lon) map, dedup by first seen
    std::unordered_map<std::string, std::pair<double,double>> gps_map;
    auto gps_sample = std::static_pointer_cast<arrow::StringArray>(gps_table->column(sample_idx)->chunk(0));
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

    // Extract algorithm Sample column
    auto algo_schema = algo_table->schema();
    int algo_sample_idx = algo_schema->GetFieldIndex("Sample");
    if (algo_sample_idx < 0) return 11; // output CSV should have 'Sample' header
    auto algo_sample = std::static_pointer_cast<arrow::StringArray>(algo_table->column(algo_sample_idx)->chunk(0));
    int64_t rows = algo_table->num_rows();

    // Build lat/lon arrays aligned to algorithm rows
    arrow::DoubleBuilder lat_b(pool), lon_b(pool);
    for (int64_t i = 0; i < rows; ++i) {
      std::string s = algo_sample->IsNull(i) ? std::string() : algo_sample->GetString(i);
      while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
      size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
      auto it = gps_map.find(s);
      if (it == gps_map.end()) {
        // append nulls
        ARROW_RETURN_NOT_OK(lat_b.AppendNull());
        ARROW_RETURN_NOT_OK(lon_b.AppendNull());
      } else {
        ARROW_RETURN_NOT_OK(lat_b.Append(it->second.first));
        ARROW_RETURN_NOT_OK(lon_b.Append(it->second.second));
      }
    }
    std::shared_ptr<arrow::Array> lat_arr, lon_arr;
    ARROW_RETURN_NOT_OK(lat_b.Finish(&lat_arr));
    ARROW_RETURN_NOT_OK(lon_b.Finish(&lon_arr));

    // Append as last two columns
    ARROW_ASSIGN_OR_RAISE(auto with_lat, algo_table->AddColumn(algo_table->num_columns(),
      arrow::field("latitude", arrow::float64()), lat_arr));
    ARROW_ASSIGN_OR_RAISE(auto final_tbl, with_lat->AddColumn(with_lat->num_columns(),
      arrow::field("longitude", arrow::float64()), lon_arr));

    // Write Parquet
    ARROW_ASSIGN_OR_RAISE(auto sink, arrow::io::FileOutputStream::Open(out_parquet_path));
    auto st = parquet::arrow::WriteTable(*final_tbl, pool, sink, 1024);
    if (!st.ok()) return 12;
    return 0;
  } catch (...) {
    return 99;
  }
}

}


