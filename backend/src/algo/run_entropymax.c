#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "preprocess.h"
#include "metrics.h"
#include "sweep.h"

// Simple CSV reader for your format (assumes no quoted fields, first row is header, first column is sample name)
int read_csv(const char *filename, double **data, int *rows, int *cols, char ***rownames, char ***colnames) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;

    char line[8192];
    int r = 0, c = 0;
    int max_rows = 256, max_cols = 128;

    // Allocate space
    *data = malloc(max_rows * max_cols * sizeof(double));
    *rownames = malloc(max_rows * sizeof(char*));
    *colnames = malloc(max_cols * sizeof(char*));

    // Read header
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }
    char *tok = strtok(line, ",\n");
    int col = 0;
    tok = strtok(NULL, ",\n"); // skip "Sample Name"
    while (tok) {
        (*colnames)[col++] = strdup(tok);
        tok = strtok(NULL, ",\n");
    }
    *cols = col;

    // Read data rows
    while (fgets(line, sizeof(line), fp)) {
        if (strlen(line) < 3) continue; // skip empty lines
        tok = strtok(line, ",\n");
        (*rownames)[r] = strdup(tok);
        for (col = 0; col < *cols; col++) {
            tok = strtok(NULL, ",\n");
            (*data)[r * (*cols) + col] = tok ? atof(tok) : 0.0;
        }
        r++;
        if (r >= max_rows) break;
    }
    *rows = r;
    fclose(fp);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s sample_input.csv sample_output.csv\n", argv[0]);
        return 1;
    }

    double *data = NULL;
    int rows = 0, cols = 0;
    char **rownames = NULL, **colnames = NULL;

    if (read_csv(argv[1], &data, &rows, &cols, &rownames, &colnames) != 0) {
        fprintf(stderr, "Failed to read input CSV\n");
        return 1;
    }

    // Preprocess: row proportions
    em_proportion(data, rows, cols);

    // Compute metrics
    double *Y = malloc(cols * sizeof(double));
    double tineq = 0.0;
    em_total_inequality(data, rows, cols, Y, &tineq);

    // Sweep groups 2–20
    int k_min = 2, k_max = 20;
    int metrics_cap = k_max - k_min + 1;
    em_k_metric_t *metrics = malloc(metrics_cap * sizeof(em_k_metric_t));
    int32_t *member1 = malloc(rows * sizeof(int32_t));
    double *group_means = malloc(k_max * cols * sizeof(double));
    int out_opt_k = 0;
    int perms_n = 10;
    uint64_t seed = 42;

    em_sweep_k(data, rows, cols, Y, tineq, k_min, k_max, &out_opt_k, perms_n, seed,
               metrics, metrics_cap, member1, group_means);

    // Write output summary (simple version)
    FILE *out = fopen(argv[2], "w");
    if (!out) {
        fprintf(stderr, "Failed to open output file\n");
        return 1;
    }
    fprintf(out, "%s, %d samples\n", argv[1], rows);
    fprintf(out, "Data groupings for %d groups\n", out_opt_k);
    for (int i = 0; i < rows; ++i) {
        fprintf(out, "%s,Group %d\n", rownames[i], member1[i]);
    }
    fprintf(out, "\nGroup means:\n");
    for (int g = 0; g < out_opt_k; ++g) {
        fprintf(out, "Group %d:", g);
        for (int j = 0; j < cols; ++j) {
            fprintf(out, " %.4f", group_means[g * cols + j]);
        }
        fprintf(out, "\n");
    }
    fclose(out);

    // Free memory
    for (int i = 0; i < rows; ++i) free(rownames[i]);
    for (int j = 0; j < cols; ++j) free(colnames[j]);
    free(rownames); free(colnames); free(data); free(Y); free(metrics); free(member1); free(group_means);

    printf("Done. Output written to %s\n", argv[2]);
    return 0;
}