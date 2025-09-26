#include <arrow/api.h>
#include <arrow/io/api.h>
#include <parquet/arrow/reader.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iostream>
#include <unordered_map>

static std::vector<std::string> split_csv_header(const std::string& line) {
  std::vector<std::string> out;
  std::stringstream ss(line);
  std::string tok;
  while (std::getline(ss, tok, ',')) out.push_back(tok);
  return out;
}

int main() {
  const char* csv_path = "data/processed/sample_outputt.csv";
  const char* pq_path  = "data/parquet/output.parquet";

  // Read CSV header and count rows
  std::ifstream fin(csv_path, std::ios::in);
  if (!fin.is_open()) {
    std::cerr << "FAIL: cannot open " << csv_path << "\n";
    return 1;
  }
  std::string header_line;
  if (!std::getline(fin, header_line)) {
    std::cerr << "FAIL: cannot read header from CSV\n";
    return 1;
  }
  auto csv_cols = split_csv_header(header_line);
  size_t csv_rows = 0;
  {
    std::string tmp;
    while (std::getline(fin, tmp)) ++csv_rows;
  }

  // Read Parquet schema and rows
  auto infile_res = arrow::io::ReadableFile::Open(pq_path);
  if (!infile_res.ok()) {
    std::cerr << "FAIL: cannot open parquet: " << pq_path << "\n";
    return 2;
  }
  std::shared_ptr<arrow::io::ReadableFile> inp = *infile_res;

  parquet::arrow::FileReaderBuilder builder;
  auto st_open = builder.Open(inp);
  if (!st_open.ok()) {
    std::cerr << "FAIL: FileReaderBuilder.Open failed\n";
    return 3;
  }
  std::unique_ptr<parquet::arrow::FileReader> reader;
  auto st_build = builder.Build(&reader);
  if (!st_build.ok()) {
    std::cerr << "FAIL: FileReaderBuilder.Build failed\n";
    return 3;
  }

  std::shared_ptr<arrow::Schema> schema;
  auto st_schema = reader->GetSchema(&schema);
  if (!st_schema.ok()) {
    std::cerr << "FAIL: GetSchema failed\n";
    return 3;
  }
  const auto& names = schema->field_names();
  int64_t pq_rows = reader->parquet_reader()->metadata()->num_rows();

  if (names.size() < 3) {
    std::cerr << "FAIL: parquet has too few columns\n";
    return 4;
  }

  // Frontend expectations
  if (names[0] != "Group" || names[1] != "Sample") {
    std::cerr << "FAIL: first two columns must be [Group, Sample], got ['" << names[0] << "', '" << names[1] << "']\n";
    return 5;
  }
  const std::string& c_k   = names[names.size()-3];
  const std::string& c_lat = names[names.size()-2];
  const std::string& c_lon = names[names.size()-1];
  if (c_k != "K" || c_lat != "latitude" || c_lon != "longitude") {
    std::cerr << "FAIL: tail columns must be [K, latitude, longitude], got ['"
              << c_k << "', '" << c_lat << "', '" << c_lon << "']\n";
    return 6;
  }

  // Row parity
  if (static_cast<int64_t>(csv_rows) != pq_rows) {
    std::cerr << "FAIL: row count mismatch csv=" << csv_rows << " parquet=" << pq_rows << "\n";
    return 7;
  }

  // Remaining column set parity: Parquet without K/lat/lon must equal CSV without 'K', ignoring order
  std::unordered_map<std::string,int> need;
  for (const auto& c : csv_cols) {
    if (c == "K") continue; // K moves to tail
    need[c] += 1;
  }
  for (size_t i = 0; i < names.size(); ++i) {
    if (i == names.size()-3 || i == names.size()-2 || i == names.size()-1) continue; // skip K, lat, lon at tail
    const auto& n = names[i];
    auto it = need.find(n);
    if (it == need.end()) {
      std::cerr << "FAIL: unexpected parquet column '" << n << "' at index " << i << "\n";
      return 8;
    }
    if (--(it->second) == 0) need.erase(it);
  }
  if (!need.empty()) {
    std::cerr << "FAIL: missing columns present in CSV but not in Parquet: ";
    for (auto& kv : need) std::cerr << kv.first << "(" << kv.second << ") ";
    std::cerr << "\n";
    return 9;
  }

  std::cout << "OK: Parquet matches frontend schema (Group, Sample, ..., K, latitude, longitude) and row counts" << std::endl;
  return 0;
}


