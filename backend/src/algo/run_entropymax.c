// NOTE: Minimal CSV loader with safety checks (no quoted fields). First header column is sample_id.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "preprocess.h"
#include "metrics.h"
#include "sweep.h"

static void rstrip_newline(char *s) {
    if (!s) return;
    size_t n = strlen(s);
    while (n > 0 && (s[n-1] == '\n' || s[n-1] == '\r')) { s[n-1] = '\0'; n--; }
}

int read_csv(const char *filename, double **data, int *rows, int *cols, char ***rownames, char ***colnames) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;

    char line[16384];
    char *saveptr = NULL;

    // Read header to determine column count
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }
    rstrip_newline(line);

    int header_cols = 0;
    char *tmp = line;
    char *tok = strtok_r(tmp, ",", &saveptr);
    if (!tok) { fclose(fp); return -1; }
    // First header token is sample_id; skip storing
    while ((tok = strtok_r(NULL, ",", &saveptr)) != NULL) header_cols++;
    if (header_cols <= 0) { fclose(fp); return -1; }

    *cols = header_cols;

    // Allocate colnames and re-tokenize header to capture names
    *colnames = (char**)calloc((size_t)header_cols, sizeof(char*));
    // Re-scan original header line
    // Restore saveptr by tokenizing again
    saveptr = NULL; tok = strtok_r(line, ",", &saveptr); // sample_id header
    for (int j = 0; j < header_cols; j++) {
        tok = strtok_r(NULL, ",", &saveptr);
        if (!tok) { fclose(fp); return -1; }
        (*colnames)[j] = strdup(tok);
    }

    // Prepare dynamic row storage
    int cap_rows = 512;
    *rows = 0;
    *rownames = (char**)calloc((size_t)cap_rows, sizeof(char*));
    *data = (double*)calloc((size_t)cap_rows * (size_t)(*cols), sizeof(double));
    if (!*rownames || !*data) { fclose(fp); return -1; }

    // Read data rows
    while (fgets(line, sizeof(line), fp)) {
        rstrip_newline(line);
        if (line[0] == '\0') continue;

        // Grow rows if needed
        if (*rows >= cap_rows) {
            int new_cap = cap_rows * 2;
            char **new_rows = (char**)realloc(*rownames, (size_t)new_cap * sizeof(char*));
            double *new_data = (double*)realloc(*data, (size_t)new_cap * (size_t)(*cols) * sizeof(double));
            if (!new_rows || !new_data) { fclose(fp); return -1; }
            *rownames = new_rows; *data = new_data; cap_rows = new_cap;
        }

        saveptr = NULL;
        tok = strtok_r(line, ",", &saveptr);
        if (!tok) continue;
        (*rownames)[*rows] = strdup(tok);
        for (int j = 0; j < *cols; j++) {
            tok = strtok_r(NULL, ",", &saveptr);
            (*data)[(size_t)(*rows) * (size_t)(*cols) + (size_t)j] = tok ? atof(tok) : 0.0;
        }
        (*rows)++;
    }

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

    // Preprocess: row proportions then grand-total percent (to match reference output)
    em_proportion(data, rows, cols);
    em_gdtl_percent(data, rows, cols);

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

    int rc = em_sweep_k(data, rows, cols, Y, tineq, k_min, k_max, &out_opt_k, perms_n, seed,
                        metrics, metrics_cap, member1, group_means);
    if (rc <= 0) {
        fprintf(stderr, "Sweep failed or returned no metrics (rc=%d)\n", rc);
        return 2;
    }

    // Locate metrics entry for the chosen k
    double best_bineq = 0.0, best_rs = 0.0, best_ch = 0.0, best_sst = 0.0, best_sse = 0.0;
    for (int mi = 0; mi < rc; ++mi) {
        if (metrics[mi].nGrpDum == out_opt_k) {
            best_bineq = metrics[mi].fCHDum; // NOTE: stored as bineq in current impl
            best_rs    = metrics[mi].fRs;
            best_sst   = metrics[mi].fSST;
            best_sse   = metrics[mi].fSSE;
            best_ch    = metrics[mi].fCHF;   // NOTE: stored as CH in current impl
            break;
        }
    }

    // Write CSV matching augmented layout (sans Latitude,Longitude) with 7dp
    FILE *out = fopen(argv[2], "w");
    if (!out) {
        fprintf(stderr, "Failed to open output file\n");
        return 1;
    }

    // Header
    fprintf(out, "Group,Sample");
    for (int j = 0; j < cols; ++j) {
        fprintf(out, ",%s", colnames && colnames[j] ? colnames[j] : "var");
    }
    fprintf(out, ",Total Inequality,Between Region Inequality,Total Sum Of Squares,Within Group Sum Of Squares,Calinski-Harabasz pseudo-F statistic,%% Explained,K\n");

    // Rows
    for (int i = 0; i < rows; ++i) {
        // 1-based group for compatibility
        fprintf(out, "%d,%s", member1[i] + 1, rownames && rownames[i] ? rownames[i] : "");
        for (int j = 0; j < cols; ++j) {
            fprintf(out, ",%.7f", data[(size_t)i * (size_t)cols + (size_t)j]);
        }
        fprintf(out, ",%.7f,%.7f,%.7f,%.7f,%.7f,%.7f,%d\n",
                tineq, best_bineq, best_sst, best_sse, best_ch, best_rs, out_opt_k);
    }
    fclose(out);

    // Free memory
    for (int i = 0; i < rows; ++i) free(rownames[i]);
    for (int j = 0; j < cols; ++j) free(colnames[j]);
    free(rownames); free(colnames); free(data); free(Y); free(metrics); free(member1); free(group_means);

    printf("Done. Output written to %s\n", argv[2]);
    return 0;
}
