// NOTE: Minimal CSV loader with safety checks (no quoted fields). First header column is sample_id.
#include "run_entropymax.h"
#include "preprocess.h"
#include "metrics.h"
#include "sweep.h"
#include "grouping.h"

static void rstrip_newline(char *s) {
    if (!s) return;
    size_t n = strlen(s);
    while (n > 0 && (s[n-1] == '\n' || s[n-1] == '\r')) { s[n-1] = '\0'; n--; }
}

// Read header-driven bin labels from the input CSV

int read_csv(const char *filename, double **data, int *rows, int *cols, char ***rownames, char ***colnames, char **sample_header_out, char ***raw_values_out) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;

    char line[16384];
    char *saveptr = NULL;

    // Read header and derive column names from it
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }
    rstrip_newline(line);
    char *saveptr_hdr = NULL;
    char *tok_hdr = strtok_r(line, ",", &saveptr_hdr);
    if (!tok_hdr) { fclose(fp); return -1; }
    if (sample_header_out) { *sample_header_out = strdup(tok_hdr); }
    // Count remaining comma-separated tokens for bins
    int hdr_bins_cap = 128;
    int hdr_bins_count = 0;
    char **hdr_bins = (char**)calloc((size_t)hdr_bins_cap, sizeof(char*));
    while ((tok_hdr = strtok_r(NULL, ",", &saveptr_hdr)) != NULL) {
        if (hdr_bins_count >= hdr_bins_cap) {
            int new_cap = hdr_bins_cap * 2;
            char **new_bins = (char**)realloc(hdr_bins, (size_t)new_cap * sizeof(char*));
            if (!new_bins) { fclose(fp); free(hdr_bins); return -1; }
            hdr_bins = new_bins; hdr_bins_cap = new_cap;
        }
        hdr_bins[hdr_bins_count++] = strdup(tok_hdr);
    }
    *cols = hdr_bins_count;
    *colnames = (char**)calloc((size_t)(*cols), sizeof(char*));
    for (int j = 0; j < *cols; ++j) {
        (*colnames)[j] = hdr_bins[j];
    }

    // Prepare dynamic row storage
    int cap_rows = 512;
    *rows = 0;
    *rownames = (char**)calloc((size_t)cap_rows, sizeof(char*));
    *data = (double*)calloc((size_t)cap_rows * (size_t)(*cols), sizeof(double));
    char **raw_values = NULL;
    if (raw_values_out) {
        raw_values = (char**)calloc((size_t)cap_rows * (size_t)(*cols), sizeof(char*));
        if (!raw_values) { fclose(fp); return -1; }
    }
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
            char **new_raw = raw_values ? (char**)realloc(raw_values, (size_t)new_cap * (size_t)(*cols) * sizeof(char*)) : NULL;
            if (!new_rows || !new_data || (raw_values && !new_raw)) { fclose(fp); return -1; }
            *rownames = new_rows; *data = new_data; if (raw_values) raw_values = new_raw; cap_rows = new_cap;
        }

        saveptr = NULL;
        char *tok = strtok_r(line, ",", &saveptr);
        if (!tok) continue;
        (*rownames)[*rows] = strdup(tok);
        for (int j = 0; j < *cols; j++) {
            tok = strtok_r(NULL, ",", &saveptr);
            (*data)[(size_t)(*rows) * (size_t)(*cols) + (size_t)j] = tok ? atof(tok) : 0.0;
            if (raw_values) {
                raw_values[(size_t)(*rows) * (size_t)(*cols) + (size_t)j] = tok ? strdup(tok) : strdup("0");
            }
        }
        (*rows)++;
    }

    fclose(fp);
    if (raw_values_out) { *raw_values_out = raw_values; }
    return 0;
}

int main(int argc, char **argv) {
    (void)argc; (void)argv; // ignore CLI args; enforce fixed IO paths per requirements

    const char *fixed_input_path = "data/input.csv";
    const char *fixed_output_path = "data/processed/sample_outputt.csv";

    double *data = NULL; // raw data as read
    int rows = 0, cols = 0;
    char **rownames = NULL, **colnames = NULL; char *sample_header = NULL;
    char **raw_values = NULL;

    if (read_csv(fixed_input_path, &data, &rows, &cols, &rownames, &colnames, &sample_header, &raw_values) != 0) {
        fprintf(stderr, "Failed to read input CSV\n");
        return 1;
    }

    // Make a processed working copy for algorithm; keep raw data for output
    double *data_proc = malloc((size_t)rows * (size_t)cols * sizeof(double));
    if (!data_proc) {
        fprintf(stderr, "OOM\n");
        return 1;
    }
    memcpy(data_proc, data, (size_t)rows * (size_t)cols * sizeof(double));

    // Preprocess for algorithm only (grand-total percent only)
    em_gdtl_percent(data_proc, rows, cols);

    // Compute metrics
    double *Y = malloc(cols * sizeof(double));
    double tineq = 0.0;
    em_total_inequality(data_proc, rows, cols, Y, &tineq);

    // Sweep groups 2–20
    int k_min = 2, k_max = 20;
    int metrics_cap = k_max - k_min + 1;
    em_k_metric_t *metrics = malloc(metrics_cap * sizeof(em_k_metric_t));
    int32_t *member1 = malloc(rows * sizeof(int32_t));
    double *group_means = malloc(k_max * cols * sizeof(double));
    int32_t *all_member1 = malloc((size_t)metrics_cap * (size_t)rows * sizeof(int32_t));
    int out_opt_k = 0;
    int perms_n = 0; // disable permutations for deterministic output equivalence
    uint64_t seed = 42;

    int rc = em_sweep_k(data_proc, rows, cols, Y, tineq, k_min, k_max, &out_opt_k, perms_n, seed,
                        metrics, metrics_cap, member1, group_means, all_member1);
    if (rc <= 0) {
        fprintf(stderr, "Sweep failed or returned no metrics (rc=%d)\n", rc);
        return 2;
    }

    // Write CSV matching VB6 composite layout for every k (group blocks + per-k summary)
    FILE *out = fopen(fixed_output_path, "w");
    if (!out) {
        fprintf(stderr, "Failed to open output file\n");
        return 1;
    }

    // Single header line at top
    fprintf(out, "K,Group,Sample");
    for (int j = 0; j < cols; ++j) {
        fprintf(out, ",%s", colnames && colnames[j] ? colnames[j] : "var");
    }
    fprintf(out, ",%% explained,Total inequality,Between region inequality,Total sum of squares,Within group sum of squares,Calinski-Harabasz pseudo-F statistic\n");

    for (int mi = 0; mi < rc; ++mi) {
        int k = metrics[mi].nGrpDum;
        const int32_t *member_k = all_member1 + (size_t)mi * (size_t)rows;

        // Emit groups for this k (using precomputed member_k)
        for (int g = 1; g <= k; ++g) {
            for (int i = 0; i < rows; ++i) {
                if (member_k[i] + 1 != g) continue;
                fprintf(out, "%d,%d,%s", k, g, rownames && rownames[i] ? rownames[i] : "");
                for (int j = 0; j < cols; ++j) {
                    const char *tok = raw_values ? raw_values[(size_t)i * (size_t)cols + (size_t)j] : NULL;
                    if (tok) {
                        fprintf(out, ",%s", tok);
                    } else {
                        fprintf(out, ",%G", data[(size_t)i * (size_t)cols + (size_t)j]);
                    }
                }
                // Append metrics per row for this k
                fprintf(out, ",%G,%G,%G,%G,%G,%G",
                        metrics[mi].fRs,
                        tineq,
                        metrics[mi].fBetween,
                        metrics[mi].fSST,
                        metrics[mi].fSSE,
                        metrics[mi].fCHDum);
                fprintf(out, "\n");
            }
        }
    }
    fclose(out);

    // Free memory
    for (int i = 0; i < rows; ++i) free(rownames[i]);
    for (int j = 0; j < cols; ++j) free(colnames[j]);
    if (raw_values) {
        for (int i = 0; i < rows * cols; ++i) free(raw_values[i]);
        free(raw_values);
    }
    free(rownames); free(colnames); free(sample_header); free(data); free(Y); free(metrics); free(member1); free(group_means); free(all_member1); free(data_proc);

    printf("Done. Output written to %s\n", fixed_output_path);
    return 0;
}
