#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef struct {
  int32_t num_samples;
  int32_t num_variables;
  bool row_proportions;
  bool grand_total_norm;
  bool ch_permutations;
  int32_t ch_permutations_n;
  uint64_t rng_seed;
} em_config_t;

typedef struct {
  int32_t optimal_k;
  // more fields TBD
} em_result_t;

// optional future convenience API
int em_run_from_csv(const char *csv_path, const char *parquet_out_path, const em_config_t *cfg);

