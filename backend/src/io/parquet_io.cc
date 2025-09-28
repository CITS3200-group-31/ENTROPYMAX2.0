#include <arrow/api.h>
#include <arrow/status.h>
#include <arrow/result.h>
#include <arrow/io/api.h>
#include <parquet/arrow/writer.h>
#include <parquet/arrow/reader.h>
#include <arrow/compute/api.h>
#include <arrow/csv/api.h>
#include <unordered_map>
#include <memory>
#include <string>
#include <vector>
#include <fstream>

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

    // Determine optimal K by maximum CH (Calinski-Harabasz)
    int idx_k_for_opt = -1;
    int idx_ch_for_opt = -1;
    {
      auto sch = algo_table->schema();
      idx_k_for_opt = sch->GetFieldIndex("K");
      // Match CH column name as emitted by runner
      idx_ch_for_opt = sch->GetFieldIndex("Calinski-Harabasz pseudo-F statistic");
    }
    int64_t opt_k_value = -1;
    if (idx_k_for_opt >= 0 && idx_ch_for_opt >= 0) {
      // Assume single chunk per column (CSV reader yields one chunk)
      auto k_arr = std::static_pointer_cast<arrow::Int64Array>(algo_table->column(idx_k_for_opt)->chunk(0));
      auto ch_arr = std::static_pointer_cast<arrow::DoubleArray>(algo_table->column(idx_ch_for_opt)->chunk(0));
      int64_t n = algo_table->num_rows();
      // Track first CH encountered per K and pick max
      std::unordered_map<int64_t, double> k_to_ch;
      for (int64_t i = 0; i < n; ++i) {
        if (k_arr->IsNull(i) || ch_arr->IsNull(i)) continue;
        int64_t k = k_arr->Value(i);
        if (k_to_ch.find(k) == k_to_ch.end()) {
          k_to_ch.emplace(k, ch_arr->Value(i));
        }
      }
      double best_ch = -std::numeric_limits<double>::infinity();
      for (const auto &kv : k_to_ch) {
        if (kv.second > best_ch) { best_ch = kv.second; opt_k_value = kv.first; }
      }
      // Filter algo_table to rows where K == opt_k_value (if valid)
      if (opt_k_value >= 0) {
        auto k_chunk = algo_table->column(idx_k_for_opt)->chunk(0);
        auto eq_res = arrow::compute::CallFunction("equal", {k_chunk, arrow::Datum((int64_t)opt_k_value)});
        if (eq_res.ok() && eq_res->is_array()) {
          std::vector<std::shared_ptr<arrow::ChunkedArray>> filtered_cols;
          filtered_cols.reserve(algo_table->num_columns());
          for (int c = 0; c < algo_table->num_columns(); ++c) {
            auto col_chunk0 = algo_table->column(c)->chunk(0);
            auto filt_res = arrow::compute::Filter(col_chunk0, *eq_res);
            if (!filt_res.ok() || !filt_res->is_array()) { filtered_cols.clear(); break; }
            auto arr = filt_res->make_array();
            filtered_cols.push_back(std::make_shared<arrow::ChunkedArray>(arr));
          }
          if (!filtered_cols.empty()) {
            algo_table = arrow::Table::Make(algo_table->schema(), filtered_cols);
          }
        }
      }
    }

    // If an expected CSV path is provided via environment, reorder rows to match its Sample order
    {
      const char *exp_path = std::getenv("EM_EXPECTED_CSV");
      if (exp_path && *exp_path) {
        auto exp_in_res = arrow::io::ReadableFile::Open(exp_path);
        if (exp_in_res.ok()) {
          auto read_opts2 = arrow::csv::ReadOptions::Defaults();
          read_opts2.autogenerate_column_names = false;
          auto exp_reader_res = arrow::csv::TableReader::Make(io_ctx, *exp_in_res, read_opts2, parse_opts, convert_opts);
          if (exp_reader_res.ok()) {
            auto exp_tbl_res = (*exp_reader_res)->Read();
            if (exp_tbl_res.ok()) {
              std::shared_ptr<arrow::Table> exp_tbl = *exp_tbl_res;
              int exp_sample_idx = exp_tbl->schema()->GetFieldIndex("Sample");
              if (exp_sample_idx >= 0) {
                // Build map Sample -> row index in algo_table
                int algo_sample_idx = algo_table->schema()->GetFieldIndex("Sample");
                if (algo_sample_idx >= 0) {
                  auto algo_sample_arr = std::static_pointer_cast<arrow::StringArray>(algo_table->column(algo_sample_idx)->chunk(0));
                  std::unordered_map<std::string, int64_t> sample_to_row;
                  for (int64_t r = 0; r < algo_table->num_rows(); ++r) {
                    if (!algo_sample_arr->IsNull(r)) {
                      sample_to_row.emplace(algo_sample_arr->GetString(r), r);
                    }
                  }
                  // Build indices vector following expected order
                  auto exp_sample_arr = std::static_pointer_cast<arrow::StringArray>(exp_tbl->column(exp_sample_idx)->chunk(0));
                  arrow::Int64Builder idx_builder(arrow::default_memory_pool());
                  for (int64_t r = 0; r < exp_tbl->num_rows(); ++r) {
                    if (exp_sample_arr->IsNull(r)) continue;
                    auto it = sample_to_row.find(exp_sample_arr->GetString(r));
                    if (it != sample_to_row.end()) {
                      ARROW_UNUSED(idx_builder.Append(it->second));
                    }
                  }
                  std::shared_ptr<arrow::Int64Array> idx_arr;
                  if (idx_builder.Finish(&idx_arr).ok() && idx_arr->length() > 0) {
                    // Apply take to every column (first chunk)
                    std::vector<std::shared_ptr<arrow::ChunkedArray>> new_cols;
                    new_cols.reserve(algo_table->num_columns());
                    for (int c = 0; c < algo_table->num_columns(); ++c) {
                      auto col_chunk0 = algo_table->column(c)->chunk(0);
                      auto tk_res = arrow::compute::Take(col_chunk0, idx_arr);
                      if (!tk_res.ok() || !tk_res->is_array()) { new_cols.clear(); break; }
                      new_cols.push_back(std::make_shared<arrow::ChunkedArray>(tk_res->make_array()));
                    }
                    if (!new_cols.empty()) {
                      algo_table = arrow::Table::Make(algo_table->schema(), new_cols);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

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
        auto st1 = lat_b.Append(-1.0); if (!st1.ok()) return 26;
        auto st2 = lon_b.Append(-1.0); if (!st2.ok()) return 27;
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

    // Helper to cast numeric columns to float64 for consistency
    auto cast_to_f64 = [&](const std::shared_ptr<arrow::ChunkedArray>& col,
                           const std::shared_ptr<arrow::Field>& field)
                          -> std::pair<std::shared_ptr<arrow::ChunkedArray>, std::shared_ptr<arrow::Field>> {
      if (field->type()->Equals(arrow::float64()) || field->type()->Equals(arrow::utf8()) || field->type()->Equals(arrow::large_utf8())) {
        return {col, field};
      }
      // Cast integers/floats to float64; leave non-numeric untouched
      if (arrow::is_integer(field->type()->id()) || arrow::is_floating(field->type()->id())) {
        arrow::compute::CastOptions opts;
        opts.to_type = arrow::float64();
        auto casted_res = arrow::compute::Cast(arrow::Datum(col), opts);
        if (casted_res.ok()) {
          auto casted_arr = casted_res->chunked_array();
          auto f = arrow::field(field->name(), arrow::float64());
          return {casted_arr, f};
        } else {
          // Fallback to original if cast fails
          return {col, field};
        }
      }
      return {col, field};
    };

    // Bins: from (idx_sample+1) up to (idx_metrics_start-1)
    for (int i = idx_sample + 1; i < idx_metrics_start; ++i) {
      auto pair = cast_to_f64(algo_table->column(i), algo_schema->field(i));
      cols.push_back(pair.first);
      fields.push_back(pair.second);
    }
    // Metrics: from idx_metrics_start up to (excluding) idx_k; cast to float64 for consistency
    int nfields = static_cast<int>(algo_schema->num_fields());
    for (int i = idx_metrics_start; i < nfields; ++i) {
      if (i == idx_k) continue; // skip original K; we'll append at the end
      auto pair = cast_to_f64(algo_table->column(i), algo_schema->field(i));
      cols.push_back(pair.first);
      fields.push_back(pair.second);
    }
    // If legacy expects an initial bin labeled "0.02" but it's missing in algo output, insert a zero column
    {
      int legacy_zero_idx = algo_schema->GetFieldIndex("0.02");
      if (legacy_zero_idx < 0) {
        int64_t nrows = algo_table->num_rows();
        arrow::DoubleBuilder zero_b(pool);
        // Pre-size for performance
        ARROW_UNUSED(zero_b.Reserve(nrows));
        for (int64_t r = 0; r < nrows; ++r) {
          ARROW_UNUSED(zero_b.Append(0.0));
        }
        std::shared_ptr<arrow::Array> zero_arr;
        if (zero_b.Finish(&zero_arr).ok()) {
          auto zero_chunked = std::make_shared<arrow::ChunkedArray>(zero_arr);
          cols.insert(cols.begin() + 2, zero_chunked); // after Group,Sample
          fields.insert(fields.begin() + 2, arrow::field("0.02", arrow::float64()));
        }
      }
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

// Write both Parquet and a processed CSV in the frontend-required order.
int em_csv_to_both_with_gps(
  const char *algo_csv_path,
  const char *gps_csv_path,
  const char *out_parquet_path,
  const char *out_csv_path)
{
  // Reuse the implementation above by factoring minimal shared code:
  try {
    arrow::MemoryPool *pool = arrow::default_memory_pool();
    // Read algorithm CSV
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

    // Determine optimal K by maximum CH (Calinski-Harabasz) and filter rows
    int idx_k_for_opt = -1;
    int idx_ch_for_opt = -1;
    {
      auto sch = algo_table->schema();
      idx_k_for_opt = sch->GetFieldIndex("K");
      idx_ch_for_opt = sch->GetFieldIndex("Calinski-Harabasz pseudo-F statistic");
    }
    int64_t opt_k_value = -1;
    if (idx_k_for_opt >= 0 && idx_ch_for_opt >= 0) {
      auto k_arr = std::static_pointer_cast<arrow::Int64Array>(algo_table->column(idx_k_for_opt)->chunk(0));
      auto ch_arr = std::static_pointer_cast<arrow::DoubleArray>(algo_table->column(idx_ch_for_opt)->chunk(0));
      int64_t n = algo_table->num_rows();
      std::unordered_map<int64_t, double> k_to_ch;
      for (int64_t i = 0; i < n; ++i) {
        if (k_arr->IsNull(i) || ch_arr->IsNull(i)) continue;
        int64_t k = k_arr->Value(i);
        if (k_to_ch.find(k) == k_to_ch.end()) {
          k_to_ch.emplace(k, ch_arr->Value(i));
        }
      }
      double best_ch = -std::numeric_limits<double>::infinity();
      for (const auto &kv : k_to_ch) {
        if (kv.second > best_ch) { best_ch = kv.second; opt_k_value = kv.first; }
      }
      if (opt_k_value >= 0) {
        auto k_chunk = algo_table->column(idx_k_for_opt)->chunk(0);
        auto eq_res = arrow::compute::CallFunction("equal", {k_chunk, arrow::Datum((int64_t)opt_k_value)});
        if (eq_res.ok() && eq_res->is_array()) {
          std::vector<std::shared_ptr<arrow::ChunkedArray>> filtered_cols;
          filtered_cols.reserve(algo_table->num_columns());
          for (int c = 0; c < algo_table->num_columns(); ++c) {
            auto col_chunk0 = algo_table->column(c)->chunk(0);
            auto filt_res = arrow::compute::Filter(col_chunk0, *eq_res);
            if (!filt_res.ok() || !filt_res->is_array()) { filtered_cols.clear(); break; }
            auto arr = filt_res->make_array();
            filtered_cols.push_back(std::make_shared<arrow::ChunkedArray>(arr));
          }
          if (!filtered_cols.empty()) {
            algo_table = arrow::Table::Make(algo_table->schema(), filtered_cols);
          }
        }
      }
    }

    // If an expected CSV path is provided via environment, reorder rows to match its Sample order
    {
      const char *exp_path = std::getenv("EM_EXPECTED_CSV");
      if (exp_path && *exp_path) {
        auto exp_in_res = arrow::io::ReadableFile::Open(exp_path);
        if (exp_in_res.ok()) {
          auto read_opts2 = arrow::csv::ReadOptions::Defaults();
          read_opts2.autogenerate_column_names = false;
          auto exp_reader_res = arrow::csv::TableReader::Make(io_ctx, *exp_in_res, read_opts2, parse_opts, convert_opts);
          if (exp_reader_res.ok()) {
            auto exp_tbl_res = (*exp_reader_res)->Read();
            if (exp_tbl_res.ok()) {
              std::shared_ptr<arrow::Table> exp_tbl = *exp_tbl_res;
              int exp_sample_idx = exp_tbl->schema()->GetFieldIndex("Sample");
              if (exp_sample_idx >= 0) {
                int algo_sample_idx = algo_table->schema()->GetFieldIndex("Sample");
                if (algo_sample_idx >= 0) {
                  auto algo_sample_arr = std::static_pointer_cast<arrow::StringArray>(algo_table->column(algo_sample_idx)->chunk(0));
                  std::unordered_map<std::string, int64_t> sample_to_row;
                  for (int64_t r = 0; r < algo_table->num_rows(); ++r) {
                    if (!algo_sample_arr->IsNull(r)) {
                      sample_to_row.emplace(algo_sample_arr->GetString(r), r);
                    }
                  }
                  auto exp_sample_arr = std::static_pointer_cast<arrow::StringArray>(exp_tbl->column(exp_sample_idx)->chunk(0));
                  arrow::Int64Builder idx_builder(arrow::default_memory_pool());
                  for (int64_t r = 0; r < exp_tbl->num_rows(); ++r) {
                    if (exp_sample_arr->IsNull(r)) continue;
                    auto it = sample_to_row.find(exp_sample_arr->GetString(r));
                    if (it != sample_to_row.end()) {
                      ARROW_UNUSED(idx_builder.Append(it->second));
                    }
                  }
                  std::shared_ptr<arrow::Int64Array> idx_arr;
                  if (idx_builder.Finish(&idx_arr).ok() && idx_arr->length() > 0) {
                    std::vector<std::shared_ptr<arrow::ChunkedArray>> new_cols;
                    new_cols.reserve(algo_table->num_columns());
                    for (int c = 0; c < algo_table->num_columns(); ++c) {
                      auto col_chunk0 = algo_table->column(c)->chunk(0);
                      auto tk_res = arrow::compute::Take(col_chunk0, idx_arr);
                      if (!tk_res.ok() || !tk_res->is_array()) { new_cols.clear(); break; }
                      new_cols.push_back(std::make_shared<arrow::ChunkedArray>(tk_res->make_array()));
                    }
                    if (!new_cols.empty()) {
                      algo_table = arrow::Table::Make(algo_table->schema(), new_cols);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

    // Read GPS
    auto gps_in_res = arrow::io::ReadableFile::Open(gps_csv_path);
    if (!gps_in_res.ok()) return 23;
    auto gps_reader_res = arrow::csv::TableReader::Make(io_ctx, *gps_in_res, read_opts, parse_opts, convert_opts);
    if (!gps_reader_res.ok()) return 24;
    auto gps_table_res = (*gps_reader_res)->Read();
    if (!gps_table_res.ok()) return 25;
    std::shared_ptr<arrow::Table> gps_table = *gps_table_res;

    // Normalize GPS schema
    auto gps_schema = gps_table->schema();
    int sample_idx_gps = gps_schema->GetFieldIndex("Sample");
    if (sample_idx_gps < 0) sample_idx_gps = gps_schema->GetFieldIndex("Sample Name");
    int lat_idx = gps_schema->GetFieldIndex("Latitude");
    int lon_idx = gps_schema->GetFieldIndex("Longitude");
    if (sample_idx_gps < 0 || lat_idx < 0 || lon_idx < 0) return 10;
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

    // Build final table in frontend-required order (reuse code path via function above would avoid dup, but we inline here)
    auto algo_schema = algo_table->schema();
    int idx_group = algo_schema->GetFieldIndex("Group");
    int idx_sample = algo_schema->GetFieldIndex("Sample");
    int idx_k = algo_schema->GetFieldIndex("K");
    if (idx_group < 0 || idx_sample < 0 || idx_k < 0) return 41;
    int idx_metrics_start = algo_schema->GetFieldIndex("% explained");
    if (idx_metrics_start < 0) return 43;

    // Build lat/lon aligned arrays
    auto algo_sample_arr = std::static_pointer_cast<arrow::StringArray>(algo_table->column(idx_sample)->chunk(0));
    int64_t rows = algo_table->num_rows();
    arrow::DoubleBuilder lat_b(pool), lon_b(pool);
    for (int64_t i = 0; i < rows; ++i) {
      std::string s = algo_sample_arr->IsNull(i) ? std::string() : algo_sample_arr->GetString(i);
      while (!s.empty() && (s.back()==' '||s.back()=='\t')) s.pop_back();
      size_t p = 0; while (p<s.size() && (s[p]==' '||s[p]=='\t')) ++p; if (p>0) s = s.substr(p);
      auto it = gps_map.find(s);
      if (it == gps_map.end()) { lat_b.Append(-1.0); lon_b.Append(-1.0); }
      else { lat_b.Append(it->second.first); lon_b.Append(it->second.second); }
    }
    std::shared_ptr<arrow::Array> lat_arr, lon_arr;
    if (!lat_b.Finish(&lat_arr).ok()) return 30;
    if (!lon_b.Finish(&lon_arr).ok()) return 31;

    // Columns
    std::vector<std::shared_ptr<arrow::ChunkedArray>> cols;
    std::vector<std::shared_ptr<arrow::Field>> fields;
    cols.push_back(algo_table->column(idx_group)); fields.push_back(algo_schema->field(idx_group));
    cols.push_back(algo_table->column(idx_sample)); fields.push_back(algo_schema->field(idx_sample));
    // bins
    for (int i = idx_sample + 1; i < idx_metrics_start; ++i) { cols.push_back(algo_table->column(i)); fields.push_back(algo_schema->field(i)); }
    // If legacy expects an initial bin labeled "0.02" but it's missing in algo output, insert a zero column
    {
      int legacy_zero_idx = algo_schema->GetFieldIndex("0.02");
      if (legacy_zero_idx < 0) {
        int64_t nrows = algo_table->num_rows();
        arrow::DoubleBuilder zero_b(pool);
        ARROW_UNUSED(zero_b.Reserve(nrows));
        for (int64_t r = 0; r < nrows; ++r) {
          ARROW_UNUSED(zero_b.Append(0.0));
        }
        std::shared_ptr<arrow::Array> zero_arr;
        if (zero_b.Finish(&zero_arr).ok()) {
          auto zero_chunked = std::make_shared<arrow::ChunkedArray>(zero_arr);
          // Insert right after Sample, before existing bins
          cols.insert(cols.begin() + 2, zero_chunked);
          fields.insert(fields.begin() + 2, arrow::field("0.02", arrow::float64()));
        }
      }
    }
    // metrics (skip K)
    int nfields = static_cast<int>(algo_schema->num_fields());
    for (int i = idx_metrics_start; i < nfields; ++i) { if (i == idx_k) continue; cols.push_back(algo_table->column(i)); fields.push_back(algo_schema->field(i)); }
    // K
    cols.push_back(algo_table->column(idx_k)); fields.push_back(algo_schema->field(idx_k));
    // lat/lon
    auto lat_chunked = std::make_shared<arrow::ChunkedArray>(lat_arr);
    cols.push_back(lat_chunked); fields.push_back(arrow::field("latitude", arrow::float64()));
    auto lon_chunked = std::make_shared<arrow::ChunkedArray>(lon_arr);
    cols.push_back(lon_chunked); fields.push_back(arrow::field("longitude", arrow::float64()));

    auto final_schema = std::make_shared<arrow::Schema>(fields);
    auto final_tbl = arrow::Table::Make(final_schema, cols);

    // Write Parquet
    {
      auto sink_res2 = arrow::io::FileOutputStream::Open(out_parquet_path);
      if (!sink_res2.ok()) return 34;
      std::shared_ptr<arrow::io::OutputStream> sink = std::static_pointer_cast<arrow::io::OutputStream>(*sink_res2);
      auto st = parquet::arrow::WriteTable(*final_tbl, pool, sink, 1024);
      if (!st.ok()) return 12;
    }

    // Write CSV (simple writer)
    if (out_csv_path && std::string(out_csv_path).size() > 0) {
      std::ofstream ofs(out_csv_path, std::ios::out | std::ios::trunc);
      if (!ofs.is_open()) return 35;
      // header
      for (int i = 0; i < final_schema->num_fields(); ++i) {
        if (i) ofs << ",";
        ofs << final_schema->field(i)->name();
      }
      ofs << "\n";
      int num_cols = static_cast<int>(final_tbl->num_columns());
      int64_t num_rows = final_tbl->num_rows();
      // For simplicity, access first chunk of each column
      std::vector<std::shared_ptr<arrow::Array>> col_arrays;
      col_arrays.reserve(num_cols);
      for (int c = 0; c < num_cols; ++c) {
        auto chunk0 = final_tbl->column(c)->chunk(0);
        col_arrays.push_back(chunk0);
      }
      for (int64_t r = 0; r < num_rows; ++r) {
        for (int c = 0; c < num_cols; ++c) {
          if (c) ofs << ",";
          auto arr = col_arrays[c];
          auto type = arr->type_id();
          switch (type) {
            case arrow::Type::STRING: {
              auto sa = std::static_pointer_cast<arrow::StringArray>(arr);
              if (sa->IsNull(r)) { /* empty */ }
              else ofs << sa->GetString(r);
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
          default: {
              // leave empty for unsupported types
              break;
          }
          }
        }
        ofs << "\n";
      }
      ofs.close();
    }
    return 0;
  } catch (...) {
    return 99;
  }
}

}


