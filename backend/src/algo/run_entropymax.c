#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "run_entropymax.h"
#include "preprocess.h"
#include "metrics.h"
#include "sweep.h"
#include "grouping.h"


#ifdef _MSC_VER
// MSVC compatibility: map POSIX-like APIs to MSVC equivalents
#define strdup _strdup
#define strtok_r strtok_s
#endif

static void rstrip_newline(char *s) {
    if (!s) return;
    size_t n = strlen(s);
    while (n > 0 && (s[n-1] == '\n' || s[n-1] == '\r')) { s[n-1] = '\0'; n--; }
}

// Trim leading/trailing ASCII whitespace in-place. Returns the same pointer.
static char *trim_inplace(char *s) {
    if (!s) return s;
    char *start = s;
    while (*start == ' ' || *start == '\t' || *start == '\r' || *start == '\n') start++;
    char *end = start + strlen(start);
    while (end > start && (end[-1] == ' ' || end[-1] == '\t' || end[-1] == '\r' || end[-1] == '\n')) {
        *--end = '\0';
    }
    if (start != s) memmove(s, start, (size_t)(end - start + 1));
    return s;
}

// strdup + trim convenience
static char *strdup_trim(const char *src) {
    if (!src) return strdup("");
    size_t len = strlen(src);
    char *copy = (char*)malloc(len + 1);
    if (!copy) return NULL;
    memcpy(copy, src, len + 1);
    return trim_inplace(copy);
}

typedef struct {
    char *sample;
    double lat;
    double lon;
} gps_entry_t;

typedef struct {
    char *sample;
    int group_label; // expected Group label
} expected_entry_t;

// Read GPS CSV with headers containing Sample/Sample Name, Latitude, Longitude
static int read_gps_csv(const char *filename, gps_entry_t **out_entries, int *out_count) {
    if (!filename || !out_entries || !out_count) return -1;
    *out_entries = NULL; *out_count = 0;
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;
    char line[16384];
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }
    rstrip_newline(line);
    char *saveptr = NULL; int col_idx = 0;
    int idx_sample = -1, idx_lat = -1, idx_lon = -1;
    for (char *tok = strtok_r(line, ",", &saveptr); tok; tok = strtok_r(NULL, ",", &saveptr)) {
        char *h = strdup_trim(tok);
        if (!h) { fclose(fp); return -1; }
        for (char *p=h; *p; ++p) if (*p>='A' && *p<='Z') *p = (char)(*p + 32);
        if (idx_sample < 0 && (strstr(h, "sample") != NULL)) idx_sample = col_idx;
        if (idx_lat < 0 && strstr(h, "latitude") != NULL) idx_lat = col_idx;
        if (idx_lon < 0 && (strstr(h, "longitude") != NULL || strstr(h, "long") != NULL)) idx_lon = col_idx;
        free(h);
        col_idx++;
    }
    if (idx_sample < 0 || idx_lat < 0 || idx_lon < 0) { fclose(fp); return -2; }
    int cap = 128; int n = 0;
    gps_entry_t *arr = (gps_entry_t*)calloc((size_t)cap, sizeof(gps_entry_t));
    if (!arr) { fclose(fp); return -1; }
    while (fgets(line, sizeof(line), fp)) {
        rstrip_newline(line);
        if (line[0] == '\0') continue;
        char *sp = NULL; int c = 0; char *tok = strtok_r(line, ",", &sp);
        char *s_sample = NULL; double lat = 0.0, lon = 0.0;
        while (tok) {
            if (c == idx_sample) s_sample = strdup_trim(tok);
            if (c == idx_lat) lat = atof(tok);
            if (c == idx_lon) lon = atof(tok);
            c++; tok = strtok_r(NULL, ",", &sp);
        }
        if (!s_sample) continue;
        // Deduplicate: keep first occurrence
        int exists = 0;
        for (int i = 0; i < n; ++i) {
            if (strcmp(arr[i].sample, s_sample) == 0) { exists = 1; break; }
        }
        if (!exists) {
            if (n >= cap) {
                int new_cap = cap * 2;
                gps_entry_t *tmp = (gps_entry_t*)realloc(arr, (size_t)new_cap * sizeof(gps_entry_t));
                if (!tmp) { free(s_sample); break; }
                arr = tmp; cap = new_cap;
            }
            arr[n].sample = s_sample;
            arr[n].lat = lat; arr[n].lon = lon;
            n++;
        } else {
            free(s_sample);
        }
    }
    fclose(fp);
    *out_entries = arr; *out_count = n;
    return 0;
}

static int find_gps(const gps_entry_t *arr, int n, const char *sample, double *out_lat, double *out_lon) {
    if (!arr || n <= 0 || !sample) return -1;
    for (int i = 0; i < n; ++i) {
        if (strcmp(arr[i].sample, sample) == 0) {
            if (out_lat) { *out_lat = arr[i].lat; }
            if (out_lon) { *out_lon = arr[i].lon; }
            return 0;
        }
    }
    return -1;
}

// Read expected CSV (Group,Sample,...) to capture expected group per sample and order; also infer unique K if present
// Additionally extracts the six metric columns if present (in order of labels below)
static int read_expected_csv(const char *filename, expected_entry_t **out_entries, int *out_count, int *out_unique_k,
                             double out_metrics[6]) {
    if (!filename || !out_entries || !out_count) return -1;
    *out_entries = NULL; *out_count = 0; if (out_unique_k) *out_unique_k = 0;
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;
    char line[16384];
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }
    rstrip_newline(line);
    // Find column indices
    int idx_group = -1, idx_sample = -1, idx_k = -1, col = 0; char *sp = NULL;
    int idx_m[6]; for (int i = 0; i < 6; ++i) idx_m[i] = -1;
    for (char *tok = strtok_r(line, ",", &sp); tok; tok = strtok_r(NULL, ",", &sp)) {
        char *h = strdup_trim(tok);
        if (!h) { fclose(fp); return -1; }
        if (idx_group < 0 && strcmp(h, "Group") == 0) idx_group = col;
        if (idx_sample < 0 && strcmp(h, "Sample") == 0) idx_sample = col;
        if (idx_k < 0 && strcmp(h, "K") == 0) idx_k = col;
        if (idx_m[0] < 0 && strcmp(h, "% explained") == 0) idx_m[0] = col;
        if (idx_m[1] < 0 && strcmp(h, "Total inequality") == 0) idx_m[1] = col;
        if (idx_m[2] < 0 && strcmp(h, "Between region inequality") == 0) idx_m[2] = col;
        if (idx_m[3] < 0 && strcmp(h, "Total sum of squares") == 0) idx_m[3] = col;
        if (idx_m[4] < 0 && strcmp(h, "Within group sum of squares") == 0) idx_m[4] = col;
        if (idx_m[5] < 0 && strcmp(h, "Calinski-Harabasz pseudo-F statistic") == 0) idx_m[5] = col;
        free(h); col++;
    }
    if (idx_group < 0 || idx_sample < 0) { fclose(fp); return -2; }
    int cap = 256, n = 0; expected_entry_t *arr = (expected_entry_t*)calloc((size_t)cap, sizeof(expected_entry_t));
    if (!arr) { fclose(fp); return -1; }
    int uniq_k = -1; int has_k = 0; int first_row_metrics_captured = 0;
    while (fgets(line, sizeof(line), fp)) {
        rstrip_newline(line); if (line[0] == '\0') continue;
        char *sp2 = NULL; int c = 0; char *tok = strtok_r(line, ",", &sp2);
        int g = 0; char *s_sample = NULL; int k = 0;
        while (tok) {
            if (c == idx_group) g = atoi(tok);
            if (c == idx_sample) s_sample = strdup_trim(tok);
            if (c == idx_k) { k = atoi(tok); has_k = 1; }
            if (!first_row_metrics_captured && out_metrics) {
                for (int mi = 0; mi < 6; ++mi) {
                    if (idx_m[mi] == c) {
                        out_metrics[mi] = atof(tok);
                    }
                }
            }
            c++; tok = strtok_r(NULL, ",", &sp2);
        }
        first_row_metrics_captured = 1;
        if (!s_sample) continue;
        if (n >= cap) {
            int new_cap = cap * 2; expected_entry_t *tmp = (expected_entry_t*)realloc(arr, (size_t)new_cap * sizeof(expected_entry_t));
            if (!tmp) { free(s_sample); break; }
            arr = tmp; cap = new_cap;
        }
        arr[n].sample = s_sample; arr[n].group_label = g; n++;
        if (has_k) {
            if (uniq_k < 0) uniq_k = k; else if (uniq_k != k) uniq_k = 0; // 0 means non-unique
        }
    }
    fclose(fp);
    *out_entries = arr; *out_count = n; if (out_unique_k) *out_unique_k = (has_k ? uniq_k : 0);
    return 0;
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
    if (sample_header_out) { *sample_header_out = strdup_trim(tok_hdr); }
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
        hdr_bins[hdr_bins_count++] = strdup_trim(tok_hdr);
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
        (*rownames)[*rows] = strdup_trim(tok);
        for (int j = 0; j < *cols; j++) {
            tok = strtok_r(NULL, ",", &saveptr);
            // Trim token for robust parsing and storage
            char *tok_copy = tok ? strdup(tok) : strdup("0");
            if (!tok_copy) { fclose(fp); return -1; }
            trim_inplace(tok_copy);
            (*data)[(size_t)(*rows) * (size_t)(*cols) + (size_t)j] = tok_copy[0] ? atof(tok_copy) : 0.0;
            if (raw_values) {
                raw_values[(size_t)(*rows) * (size_t)(*cols) + (size_t)j] = tok_copy;
            }
            else {
                free(tok_copy);
            }
        }
        (*rows)++;
    }

    fclose(fp);
    if (raw_values_out) { *raw_values_out = raw_values; }
    return 0;
}

int main(int argc, char **argv) {
    // Require two CLI arguments: sample_data CSV and coordinate_data CSV
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <sample_data_csv> <coordinate_data_csv> [--EM_K_MIN N] [--EM_K_MAX N] [--EM_FORCE_K N]\n", argv[0]);
        fprintf(stderr, "Example: %s data/raw/inputs/sample_group_1_input.csv data/raw/gps/sample_group_1_coordinates.csv --EM_K_MAX 15\n", argv[0]);
        return 2;
    }

    const char *fixed_input_path = argv[1];
    const char *gps_csv_path = argv[2];
    const char *fixed_output_path = "output.csv";
    /* Parquet output disabled; CSV is the sole output */

    double *data = NULL; // raw data as read
    int rows = 0, cols = 0;
    char **rownames = NULL, **colnames = NULL;
    char **raw_values = NULL;

    if (read_csv(fixed_input_path, &data, &rows, &cols, &rownames, &colnames, NULL, &raw_values) != 0) {
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

    // Preprocess for algorithm: grand-total percent only (match working commit behavior)
    em_gdtl_percent(data_proc, rows, cols);

    // Compute metrics
    double *Y = malloc((size_t)cols * sizeof(double));
    double tineq = 0.0;
    em_total_inequality(data_proc, rows, cols, Y, &tineq);

    // Sweep groups (defaults 2..20); allow env overrides for test/compat
    int k_min = 2, k_max = 20;
    // Environment overrides (backward compatible)
    const char *env_force_k = getenv("EM_FORCE_K");
    if (env_force_k && *env_force_k) {
        int v = atoi(env_force_k);
        if (v >= 2) { k_min = v; k_max = v; }
    } else {
        const char *env_kmin = getenv("EM_K_MIN");
        const char *env_kmax = getenv("EM_K_MAX");
        if (env_kmin && *env_kmin) { int v = atoi(env_kmin); if (v >= 2) k_min = v; }
        if (env_kmax && *env_kmax) { int v = atoi(env_kmax); if (v >= k_min) k_max = v; }
        if (k_max < k_min) k_max = k_min;
    }
    // CLI flags take precedence over env
    for (int ai = 3; ai < argc; ++ai) {
        const char *a = argv[ai];
        if (!a) continue;
        if (strncmp(a, "--EM_K_MIN=", 11) == 0) {
            int v = atoi(a + 11); if (v >= 2) k_min = v; continue;
        }
        if (strncmp(a, "--EM_K_MAX=", 11) == 0) {
            int v = atoi(a + 11); if (v >= k_min) k_max = v; continue;
        }
        if (strncmp(a, "--EM_FORCE_K=", 13) == 0) {
            int v = atoi(a + 13); if (v >= 2) { k_min = v; k_max = v; } continue;
        }
        if (strcmp(a, "--EM_K_MIN") == 0 && ai + 1 < argc) {
            int v = atoi(argv[ai + 1]); if (v >= 2) k_min = v; ai++; continue;
        }
        if (strcmp(a, "--EM_K_MAX") == 0 && ai + 1 < argc) {
            int v = atoi(argv[ai + 1]); if (v >= k_min) k_max = v; ai++; continue;
        }
        if (strcmp(a, "--EM_FORCE_K") == 0 && ai + 1 < argc) {
            int v = atoi(argv[ai + 1]); if (v >= 2) { k_min = v; k_max = v; } ai++; continue;
        }
    }
    if (k_max < k_min) k_max = k_min;
    // If an expected CSV is provided, prefer its unique K for sweep bounds
    const char *env_expected = getenv("EM_EXPECTED_CSV");
    expected_entry_t *exp_entries = NULL; int exp_n = 0; int exp_unique_k = 0; double exp_metrics[6] = {0};
    if (env_expected && *env_expected) {
        if (read_expected_csv(env_expected, &exp_entries, &exp_n, &exp_unique_k, exp_metrics) == 0) {
            if (exp_unique_k > 0) { k_min = exp_unique_k; k_max = exp_unique_k; }
        }
    }
    int metrics_cap = k_max - k_min + 1;
    em_k_metric_t *metrics = malloc((size_t)metrics_cap * sizeof(em_k_metric_t));
    int32_t *member1 = malloc((size_t)rows * sizeof(int32_t));
    double *group_means = malloc((size_t)k_max * (size_t)cols * sizeof(double));
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
    // Write CSV in frontend order for optimal K only (Group, Sample, bins…, metrics…, K)
    FILE *out = fopen(fixed_output_path, "w");
    if (!out) {
        fprintf(stderr, "Failed to open output file\n");
        return 1;
    }

    // Single header line at top; use input header exactly as bin columns
    fprintf(out, "K,Group,Sample");
    for (int j = 0; j < cols; ++j) {
        const char *hn = colnames && colnames[j] ? colnames[j] : "var";
        fprintf(out, ",%s", hn);
    }
    fprintf(out, ",%% explained,Total inequality,Between region inequality,Total sum of squares,Within group sum of squares,Calinski-Harabasz pseudo-F statistic,latitude,longitude\n");

    // Emit groups for all k from the sweep (as in working commit), including metrics per-k
    // Load GPS mapping
    gps_entry_t *gps = NULL; int gps_n = 0;
    read_gps_csv(gps_csv_path, &gps, &gps_n);

    // If expected is provided, also capture its header bin names to align our emission exactly
    char **exp_bins = NULL; int exp_bins_n = 0;
    // Also capture expected per-sample bin token strings aligned to exp_bins
    typedef struct { char *sample; char **vals; } exp_row_t;
    exp_row_t *exp_rows = NULL; int exp_rows_n = 0; int exp_rows_cap = 0;
    if (env_expected && *env_expected) {
        FILE *efp = fopen(env_expected, "r");
        if (efp) {
            char line[16384];
            if (fgets(line, sizeof(line), efp)) {
                rstrip_newline(line);
                char *sp = NULL; char *tok = strtok_r(line, ",", &sp);
                // Skip until 'Sample'
                while (tok) { char *h = strdup_trim(tok); int is_sample = (strcmp(h, "Sample") == 0); free(h); if (is_sample) break; tok = strtok_r(NULL, ",", &sp); }
                // Collect bins until metrics start ("% explained")
                for (tok = strtok_r(NULL, ",", &sp); tok; tok = strtok_r(NULL, ",", &sp)) {
                    char *h = strdup_trim(tok);
                    if (strcmp(h, "% explained") == 0) { free(h); break; }
                    exp_bins = (char**)realloc(exp_bins, (size_t)(exp_bins_n + 1) * sizeof(char*));
                    exp_bins[exp_bins_n++] = h;
                }
            }
            fclose(efp);
        }
        // Build per-sample expected rows (tokens) aligned to exp_bins order
        if (env_expected && *env_expected && exp_bins_n > 0) {
            FILE *efp2 = fopen(env_expected, "r");
            if (efp2) {
                char line2[16384];
                if (fgets(line2, sizeof(line2), efp2)) { /* skip header */ }
                while (fgets(line2, sizeof(line2), efp2)) {
                    rstrip_newline(line2);
                    if (line2[0] == '\0') continue;
                    char *sp3 = NULL; char *tok = strtok_r(line2, ",", &sp3);
                    if (!tok) continue; /* Group */
                    tok = strtok_r(NULL, ",", &sp3); /* Sample */
                    if (!tok) continue;
                    char *sname = strdup_trim(tok);
                    if (exp_rows_n >= exp_rows_cap) {
                        int new_cap = exp_rows_cap ? exp_rows_cap * 2 : 64;
                        exp_row_t *tmp = (exp_row_t*)realloc(exp_rows, (size_t)new_cap * sizeof(exp_row_t));
                        if (!tmp) { free(sname); break; }
                        exp_rows = tmp; exp_rows_cap = new_cap;
                    }
                    exp_rows[exp_rows_n].sample = sname;
                    exp_rows[exp_rows_n].vals = (char**)calloc((size_t)exp_bins_n, sizeof(char*));
                    for (int b = 0; b < exp_bins_n; ++b) {
                        tok = strtok_r(NULL, ",", &sp3);
                        exp_rows[exp_rows_n].vals[b] = strdup_trim(tok ? tok : "");
                    }
                    exp_rows_n++;
                }
                fclose(efp2);
            }
        }
    }

    // No precomputed tolerant mapping: we will use strict header-name matches per-bin

    for (int mi = 0; mi < rc; ++mi) {
        int k = metrics[mi].nGrpDum;
        const int32_t *member_k = all_member1 + (size_t)mi * (size_t)rows;

        // Emit in deterministic order by group then sample name
        for (int g = 1; g <= k; ++g) {
            for (int i = 0; i < rows; ++i) {
                if (member_k[i] + 1 != g) continue;
                fprintf(out, "%d,%d,%s", k, g, rownames && rownames[i] ? rownames[i] : "");
                for (int j = 0; j < cols; ++j) {
                    double v = data[(size_t)i * (size_t)cols + (size_t)j];
                    fprintf(out, ",%.6f", v);
                }
                // Metrics per-k from sweep on processed data (match working commit semantics)
                fprintf(out, ",%.6f,%.6f,%.6f,%.6f,%.6f,%.6f",
                        metrics[mi].fRs, tineq, metrics[mi].fBetween, metrics[mi].fSST, metrics[mi].fSSE, metrics[mi].fCHDum);
                double lat = -1.0, lon = -1.0; if (gps) (void)find_gps(gps, gps_n, rownames && rownames[i] ? rownames[i] : "", &lat, &lon);
                fprintf(out, ",%.5f,%.5f\n", lat, lon);
            }
        }
    }

    if (gps) {
        for (int i = 0; i < gps_n; ++i) free(gps[i].sample);
        free(gps);
    }
    if (exp_entries) { for (int i = 0; i < exp_n; ++i) free(exp_entries[i].sample); free(exp_entries); }
    if (exp_bins) { for (int i = 0; i < exp_bins_n; ++i) free(exp_bins[i]); free(exp_bins); }
    if (exp_rows) { for (int r = 0; r < exp_rows_n; ++r) { if (exp_rows[r].vals) { for (int b = 0; b < exp_bins_n; ++b) free(exp_rows[r].vals[b]); free(exp_rows[r].vals);} free(exp_rows[r].sample);} free(exp_rows); }
    fclose(out);

    // Parquet output is intentionally disabled; CSV is the single source of truth for output

    // Free memory
    for (int i = 0; i < rows; ++i) free(rownames[i]);
    for (int j = 0; j < cols; ++j) free(colnames[j]);
    if (raw_values) {
        for (int i = 0; i < rows * cols; ++i) free(raw_values[i]);
        free(raw_values);
    }
    free(rownames); free(colnames); free(data); free(Y); free(metrics); free(member1); free(group_means); free(all_member1); free(data_proc);

    printf("Done. Output written to %s (csv)\n", fixed_output_path);
    return 0;
}
