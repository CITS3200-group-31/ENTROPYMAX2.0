#include "parquet.h"

#include <memory>
#include <string>
#include <vector>

#include <arrow/api.h>
#include <arrow/io/api.h>
#include <arrow/csv/api.h>
#include <parquet/arrow/writer.h>
#include <parquet/arrow/reader.h>
#include <arrow/compute/api.h>

using arrow::Status;

extern "C" {

int parquet_is_available(void) { return 1; }

int parquet_write_from_csv_buffer(const char *path, const char *csv_buffer, size_t csv_size) {
  if (!path || !csv_buffer || csv_size == 0) return -1;

  auto input = std::make_shared<arrow::io::BufferReader>(reinterpret_cast<const uint8_t*>(csv_buffer), csv_size);

  auto read_options = arrow::csv::ReadOptions::Defaults();
  read_options.autogenerate_column_names = false;
  auto parse_options = arrow::csv::ParseOptions::Defaults();
  parse_options.delimiter = ',';
  auto convert_options = arrow::csv::ConvertOptions::Defaults();

  std::shared_ptr<arrow::csv::TableReader> reader;
  auto st = arrow::csv::TableReader::Make(arrow::default_memory_pool(), input, read_options, parse_options, convert_options, &reader);
  if (!st.ok()) return -1;

  std::shared_ptr<arrow::Table> table;
  st = reader->Read(&table);
  if (!st.ok()) return -1;

  auto outfile_res = arrow::io::FileOutputStream::Open(path);
  if (!outfile_res.ok()) return -1;
  std::shared_ptr<arrow::io::OutputStream> outfile = *outfile_res;

  auto wp = parquet::WriterProperties::Builder().build();
  auto arrow_props = parquet::arrow::ArrowWriterProperties::Builder().build();
  auto wst = parquet::arrow::WriteTable(*table, arrow::default_memory_pool(), outfile, 1024 * 1024, wp, arrow_props);
  if (!wst.ok()) return -1;
  return 0;
}

int parquet_write_table(const char *path, const double *data, int32_t rows, int32_t cols,
                        const char *const *colnames, const char *const *rownames) {
  if (!path || !data || rows <= 0 || cols <= 0) return -1;

  // Build columns
  arrow::FieldVector fields;
  std::vector<std::shared_ptr<arrow::Array>> arrays;

  // Row names as first column if provided
  if (rownames) {
    arrow::StringBuilder sb;
    for (int32_t i = 0; i < rows; ++i) {
      const char *s = rownames[i] ? rownames[i] : "";
      sb.Append(s);
    }
    std::shared_ptr<arrow::Array> arr;
    if (!sb.Finish(&arr).ok()) return -1;
    fields.push_back(arrow::field("Sample", arrow::utf8()));
    arrays.push_back(arr);
  }

  for (int32_t j = 0; j < cols; ++j) {
    arrow::DoubleBuilder db;
    for (int32_t i = 0; i < rows; ++i) {
      db.Append(data[(size_t)i * (size_t)cols + (size_t)j]);
    }
    std::shared_ptr<arrow::Array> arr;
    if (!db.Finish(&arr).ok()) return -1;
    std::string name = colnames && colnames[j] ? std::string(colnames[j]) : std::string("col") + std::to_string(j);
    fields.push_back(arrow::field(name, arrow::float64()));
    arrays.push_back(arr);
  }

  auto schema = std::make_shared<arrow::Schema>(fields);
  auto table = arrow::Table::Make(schema, arrays, rows);

  auto outfile_res = arrow::io::FileOutputStream::Open(path);
  if (!outfile_res.ok()) return -1;
  std::shared_ptr<arrow::io::OutputStream> outfile = *outfile_res;

  auto wp = parquet::WriterProperties::Builder().build();
  auto arrow_props = parquet::arrow::ArrowWriterProperties::Builder().build();
  auto wst = parquet::arrow::WriteTable(*table, arrow::default_memory_pool(), outfile, 1024 * 1024, wp, arrow_props);
  if (!wst.ok()) return -1;
  return 0;
}

int parquet_read_matrix_with_coords(const char *path,
                                    double **out_data, int *out_rows, int *out_cols,
                                    char ***out_rownames, char ***out_colnames,
                                    double **out_lat, double **out_lon) {
  if (!path || !out_data || !out_rows || !out_cols || !out_rownames || !out_colnames || !out_lat || !out_lon) return -1;

  auto infile_res = arrow::io::ReadableFile::Open(path);
  if (!infile_res.ok()) return -1;
  std::shared_ptr<arrow::io::ReadableFile> infile = *infile_res;

  std::unique_ptr<parquet::arrow::FileReader> reader;
  auto st = parquet::arrow::OpenFile(infile, arrow::default_memory_pool(), &reader);
  if (!st.ok()) return -1;

  std::shared_ptr<arrow::Table> table;
  if (!reader->ReadTable(&table).ok()) return -1;

  auto comb_tbl_res = table->CombineChunks(arrow::default_memory_pool());
  if (!comb_tbl_res.ok()) return -1;
  std::shared_ptr<arrow::Table> comb = *comb_tbl_res;
  std::shared_ptr<arrow::RecordBatch> batch;
  auto to_batch_res = comb->ToRecordBatch(arrow::default_memory_pool());
  if (!to_batch_res.ok()) return -1;
  batch = *to_batch_res;

  int sample_idx = batch->schema()->GetFieldIndex("Sample");
  int lat_idx = batch->schema()->GetFieldIndex("Latitude");
  int lon_idx = batch->schema()->GetFieldIndex("Longitude");

  int64_t rows = batch->num_rows();

  // Determine numeric columns (exclude Sample/Latitude/Longitude)
  std::vector<int> num_col_indices;
  std::vector<std::string> num_col_names;
  for (int i = 0; i < batch->num_columns(); ++i) {
    if (i == sample_idx || i == lat_idx || i == lon_idx) continue;
    num_col_indices.push_back(i);
    num_col_names.push_back(batch->schema()->field(i)->name());
  }
  int cols = static_cast<int>(num_col_indices.size());

  // Allocate outputs
  double *data = (double*)malloc((size_t)rows * (size_t)cols * sizeof(double));
  char **rownames = (char**)malloc((size_t)rows * sizeof(char*));
  char **colnames = (char**)malloc((size_t)cols * sizeof(char*));
  double *lat = NULL; double *lon = NULL;
  if (lat_idx >= 0 && lon_idx >= 0) {
    lat = (double*)malloc((size_t)rows * sizeof(double));
    lon = (double*)malloc((size_t)rows * sizeof(double));
  }
  if (!data || !rownames || !colnames || (lat_idx >= 0 && (!lat || !lon))) {
    free(data); free(rownames); free(colnames); if (lat) free(lat); if (lon) free(lon); return -1;
  }

  // Fill column names
  for (int j = 0; j < cols; ++j) {
    const std::string &nm = num_col_names[(size_t)j];
    colnames[j] = (char*)malloc(nm.size() + 1);
    memcpy(colnames[j], nm.c_str(), nm.size()+1);
  }

  // Access columns
  std::shared_ptr<arrow::Array> sample_arr = (sample_idx >= 0) ? batch->column(sample_idx) : nullptr;
  std::shared_ptr<arrow::Array> lat_arr = (lat_idx >= 0) ? batch->column(lat_idx) : nullptr;
  std::shared_ptr<arrow::Array> lon_arr = (lon_idx >= 0) ? batch->column(lon_idx) : nullptr;

  const arrow::StringArray *sample_str = sample_arr ? static_cast<const arrow::StringArray*>(sample_arr.get()) : nullptr;
  const arrow::DoubleArray *lat_d = lat_arr ? static_cast<const arrow::DoubleArray*>(lat_arr.get()) : nullptr;
  const arrow::DoubleArray *lon_d = lon_arr ? static_cast<const arrow::DoubleArray*>(lon_arr.get()) : nullptr;

  // Convert numeric columns to double arrays and fill data row-major
  for (int jj = 0; jj < cols; ++jj) {
    int col_idx = num_col_indices[(size_t)jj];
    auto arr = batch->column(col_idx);
    // Cast to double if needed
    std::shared_ptr<arrow::Array> dbl;
    if (arr->type_id() == arrow::Type::DOUBLE) {
      dbl = arr;
    } else {
      auto cast_res = arrow::compute::Cast(*arr, arrow::float64());
      if (!cast_res.status().ok()) return -1;
      dbl = cast_res->make_array();
    }
    const arrow::DoubleArray *col = static_cast<const arrow::DoubleArray*>(dbl.get());
    for (int64_t i = 0; i < rows; ++i) {
      double v = col->IsNull(i) ? 0.0 : col->Value(i);
      data[(size_t)i * (size_t)cols + (size_t)jj] = v;
    }
  }

  // Row names and coords
  for (int64_t i = 0; i < rows; ++i) {
    if (sample_str) {
      auto view = sample_str->IsNull(i) ? arrow::util::string_view("") : sample_str->GetView(i);
      size_t n = view.size();
      char *s = (char*)malloc(n + 1);
      memcpy(s, view.data(), n);
      s[n] = '\0';
      rownames[(size_t)i] = s;
    } else {
      rownames[(size_t)i] = (char*)malloc(1); rownames[(size_t)i][0] = '\0';
    }
    if (lat && lon) {
      lat[(size_t)i] = (lat_d && !lat_d->IsNull(i)) ? lat_d->Value(i) : 0.0;
      lon[(size_t)i] = (lon_d && !lon_d->IsNull(i)) ? lon_d->Value(i) : 0.0;
    }
  }

  *out_data = data;
  *out_rows = (int)rows;
  *out_cols = cols;
  *out_rownames = rownames;
  *out_colnames = colnames;
  *out_lat = lat;
  *out_lon = lon;
  return 0;
}

} // extern "C"


