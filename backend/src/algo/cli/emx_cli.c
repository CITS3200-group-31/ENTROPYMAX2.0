#include <stdio.h>
#include <string.h>
#include "backend.h"
#include "csv.h"
#include "algo.h"

static void usage(const char *prog){
  fprintf(stderr, "Usage: %s <input.csv> <output.parquet>\n", prog);
}

int main(int argc, char **argv){
  if(argc < 3){ usage(argv[0]); return 2; }
  em_config_t cfg = {0};
  cfg.row_proportions = true;
  cfg.grand_total_norm = true;
  cfg.ch_permutations = false;
  cfg.ch_permutations_n = 100;
  cfg.rng_seed = 42u;
  (void)cfg; // unused for now
  csv_table_t tbl = {0};
  int rc = csv_read_table(argv[1], &tbl);
  if(rc == 0){
    rc = em_run_algo(tbl.data, tbl.rows, tbl.cols, (const char* const*)tbl.colnames, (const char* const*)tbl.rownames, argv[2]);
  }
  csv_free_table(&tbl);
  if(rc != 0){
    fprintf(stderr, "Error: %d\n", rc);
  }
  return rc;
}

