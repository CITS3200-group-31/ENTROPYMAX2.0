// NOTE: Minimal CSV loader with safety checks (no quoted fields). First header column is sample_id.
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
#include <stdarg.h>
#include "preprocess.h"
#include "metrics.h"
#include "sweep.h"
#include "grouping.h"
#include "parquet.h"

// CSV sink used to optionally accumulate CSV in-memory for Parquet conversion
struct csv_sink { int use_buffer; FILE *out; char *buf; size_t size; size_t cap; };

static int sink_write(struct csv_sink *s, const char *str) {
    size_t n = strlen(str);
    if (!s->use_buffer) {
        fputs(str, s->out);
        return 0;
    }
    if (s->size + n + 1 > s->cap) {
        size_t new_cap = s->cap ? s->cap * 2 : 8192;
        while (new_cap < s->size + n + 1) new_cap *= 2;
        char *nb = (char*)realloc(s->buf, new_cap);
        if (!nb) return -1;
        s->buf = nb; s->cap = new_cap;
    }
    memcpy(s->buf + s->size, str, n);
    s->size += n;
    s->buf[s->size] = '\0';
    return 0;
}

static int sink_puts(struct csv_sink *s, const char *str) {
    return sink_write(s, str);
}

static int sink_printf(struct csv_sink *s, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    char dummy;
    va_list ap_copy;
    va_copy(ap_copy, ap);
    int needed = vsnprintf(&dummy, 0, fmt, ap_copy);
    va_end(ap_copy);
    if (needed < 0) { va_end(ap); return -1; }
    size_t size = (size_t)needed + 1;
    char *buf = (char*)malloc(size);
    if (!buf) { va_end(ap); return -1; }
    int wrote = vsnprintf(buf, size, fmt, ap);
    va_end(ap);
    if (wrote < 0) { free(buf); return -1; }
    int rc = sink_write(s, buf);
    free(buf);
    return rc;
}

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

// Simple trim helpers for matching sample names
static void trim_inplace(char *s) {
    if (!s) return;
    char *end = s + strlen(s);
    while (end > s && (end[-1] == ' ' || end[-1] == '\t' || end[-1] == '\r' || end[-1] == '\n')) {
        *--end = '\0';
    }
    while (*s == ' ' || *s == '\t') {
        memmove(s, s + 1, strlen(s));
    }
}

// Load a simple coordinates mapping CSV: header "Sample,Latitude,Longitude"
// Allocates arrays of size count; caller must free.
static int load_coords_map(const char *filename, char ***samples_out, double **lat_out, double **lon_out, int *count_out) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;

    char line[8192];
    if (!fgets(line, sizeof(line), fp)) { fclose(fp); return -1; }

    int cap = 256;
    int count = 0;
    char **samples = (char**)calloc((size_t)cap, sizeof(char*));
    double *lats = (double*)calloc((size_t)cap, sizeof(double));
    double *lons = (double*)calloc((size_t)cap, sizeof(double));
    if (!samples || !lats || !lons) { fclose(fp); free(samples); free(lats); free(lons); return -1; }

    while (fgets(line, sizeof(line), fp)) {
        char *saveptr = NULL;
        char *tok = strtok_r(line, ",", &saveptr);
        if (!tok) continue;
        char *sname = strdup(tok);
        trim_inplace(sname);
        tok = strtok_r(NULL, ",", &saveptr);
        if (!tok) { free(sname); continue; }
        double lat = atof(tok);
        tok = strtok_r(NULL, ",", &saveptr);
        if (!tok) { free(sname); continue; }
        double lon = atof(tok);

        if (count >= cap) {
            int new_cap = cap * 2;
            char **new_samples = (char**)realloc(samples, (size_t)new_cap * sizeof(char*));
            double *new_lats = (double*)realloc(lats, (size_t)new_cap * sizeof(double));
            double *new_lons = (double*)realloc(lons, (size_t)new_cap * sizeof(double));
            if (!new_samples || !new_lats || !new_lons) { free(sname); fclose(fp); return -1; }
            samples = new_samples; lats = new_lats; lons = new_lons; cap = new_cap;
        }
        samples[count] = sname; lats[count] = lat; lons[count] = lon; count++;
    }
    fclose(fp);
    *samples_out = samples; *lat_out = lats; *lon_out = lons; *count_out = count;
    return 0;
}

static int find_coords_index(const char *sample, char **map_samples, int map_count) {
    if (!sample) return -1;
    // Compare with whitespace-trimmed equality
    char *tmp = strdup(sample);
    if (!tmp) return -1;
    trim_inplace(tmp);
    for (int i = 0; i < map_count; ++i) {
        if (map_samples[i]) {
            if (strcmp(tmp, map_samples[i]) == 0) { free(tmp); return i; }
        }
    }
    free(tmp);
    return -1;
}

int main(int argc, char **argv) {
    (void)argc; (void)argv; // ignore CLI args; enforce fixed IO paths per requirements

    // Optional environment overrides for IO paths and mode
    const char *env_input_csv = getenv("EM_INPUT_CSV");
    const char *env_coords_csv = getenv("EM_COORDS_CSV");
    const char *env_output_csv = getenv("EM_OUTPUT_CSV");
    const char *env_output_mode = getenv("EM_OUTPUT"); // if set to "stdout", write to stdout
    const char *env_input_parquet = getenv("EM_INPUT_PARQUET");
    const char *env_output_parquet = getenv("EM_OUTPUT_PARQUET");

    // Prefer prepared runner CSV (from Parquet pipeline); fallback to legacy input.csv
    const char *preferred_input_path = "data/processed/input_for_runner.csv";
    const char *legacy_input_path = "data/input.csv";
    const char *coords_map_default = "data/processed/coords_map.csv";
    const char *fixed_output_default = "data/processed/sample_outputt.csv";

    double *data = NULL; // raw data as read
    int rows = 0, cols = 0;
    char **rownames = NULL, **colnames = NULL;
    char **raw_values = NULL;
    int read_rc = -1;
    double *lat_values = NULL; double *lon_values = NULL;

    if (env_input_parquet && *env_input_parquet && parquet_is_available()) {
        // Native Parquet input path (preferred if provided)
        read_rc = parquet_read_matrix_with_coords(env_input_parquet, &data, &rows, &cols, &rownames, &colnames, &lat_values, &lon_values);
        if (read_rc != 0) { fprintf(stderr, "Failed to read input Parquet\n"); return 1; }
    } else {
        // CSV fallback
        const char *input_path = env_input_csv && *env_input_csv ? env_input_csv : preferred_input_path;
        read_rc = read_csv(input_path, &data, &rows, &cols, &rownames, &colnames, NULL, &raw_values);
        if (read_rc != 0) {
            read_rc = read_csv(legacy_input_path, &data, &rows, &cols, &rownames, &colnames, NULL, &raw_values);
        }
        if (read_rc != 0) { fprintf(stderr, "Failed to read input CSV\n"); return 1; }
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
    double *Y = malloc((size_t)cols * sizeof(double));
    double tineq = 0.0;
    em_total_inequality(data_proc, rows, cols, Y, &tineq);

    // Sweep groups 2–20
    int k_min = 2, k_max = 20;
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

    // If Parquet provided coords, we don't need coords_map.csv. Otherwise try to load it.
    char **coord_samples = NULL; double *coord_lats = NULL; double *coord_lons = NULL; int coord_count = 0;
    int have_coords_from_parquet = (lat_values != NULL && lon_values != NULL);
    if (!have_coords_from_parquet) {
        const char *coords_map_path = env_coords_csv && *env_coords_csv ? env_coords_csv : coords_map_default;
        if (load_coords_map(coords_map_path, &coord_samples, &coord_lats, &coord_lons, &coord_count) != 0) {
            coord_samples = NULL; coord_lats = NULL; coord_lons = NULL; coord_count = 0;
        }
    }

    // Write CSV matching VB6 composite layout for every k (group blocks + per-k summary)
    int write_parquet = (env_output_parquet && *env_output_parquet && parquet_is_available()) ? 1 : 0;
    int to_stdout = (env_output_mode && strcmp(env_output_mode, "stdout") == 0) ? 1 : 0;
    const char *output_path = env_output_csv && *env_output_csv ? env_output_csv : fixed_output_default;
    FILE *out = NULL;
    if (!write_parquet) {
        out = to_stdout ? stdout : fopen(output_path, "w");
        if (!out) { fprintf(stderr, "Failed to open output file\n"); return 1; }
    }

    // Simple sink to write either to FILE* or to a growing memory buffer (for Parquet conversion)
    struct csv_sink sink;
    sink.use_buffer = write_parquet ? 1 : 0;
    sink.out = out;
    sink.buf = NULL;
    sink.size = 0;
    sink.cap = 0;

    // Single header line at top
    if (sink_puts(&sink, "K,Group,Sample,Latitude,Longitude") != 0) { fprintf(stderr, "OOM\n"); return 1; }
    for (int j = 0; j < cols; ++j) {
        const char *nm = (colnames && colnames[j]) ? colnames[j] : "var";
        if (sink_printf(&sink, ",%s", nm) != 0) { fprintf(stderr, "OOM\n"); return 1; }
    }
    if (sink_puts(&sink, ",% explained,Total inequality,Between region inequality,Total sum of squares,Within group sum of squares,Calinski-Harabasz pseudo-F statistic\n") != 0) { fprintf(stderr, "OOM\n"); return 1; }

    for (int mi = 0; mi < rc; ++mi) {
        int k = metrics[mi].nGrpDum;
        const int32_t *member_k = all_member1 + (size_t)mi * (size_t)rows;

        // Emit groups for this k (using precomputed member_k)
        for (int g = 1; g <= k; ++g) {
            for (int i = 0; i < rows; ++i) {
                if (member_k[i] + 1 != g) continue;
                // Coords from Parquet if present; else from coords_map
                double lat_val = 0.0, lon_val = 0.0; int has_coord = 0;
                if (have_coords_from_parquet) {
                    lat_val = lat_values[i]; lon_val = lon_values[i]; has_coord = 1;
                } else if (coord_count > 0 && rownames && rownames[i]) {
                    int idxc = find_coords_index(rownames[i], coord_samples, coord_count);
                    if (idxc >= 0) { lat_val = coord_lats[idxc]; lon_val = coord_lons[idxc]; has_coord = 1; }
                }
                if (sink_printf(&sink, "%d,%d,%s", k, g, rownames && rownames[i] ? rownames[i] : "") != 0) { fprintf(stderr, "OOM\n"); return 1; }
                if (has_coord) {
                    if (sink_printf(&sink, ",%G,%G", lat_val, lon_val) != 0) { fprintf(stderr, "OOM\n"); return 1; }
                } else {
                    if (sink_puts(&sink, ",,") != 0) { fprintf(stderr, "OOM\n"); return 1; }
                }
                for (int j = 0; j < cols; ++j) {
                    const char *tok = raw_values ? raw_values[(size_t)i * (size_t)cols + (size_t)j] : NULL;
                    if (tok) {
                        if (sink_printf(&sink, ",%s", tok) != 0) { fprintf(stderr, "OOM\n"); return 1; }
                    } else {
                        if (sink_printf(&sink, ",%G", data[(size_t)i * (size_t)cols + (size_t)j]) != 0) { fprintf(stderr, "OOM\n"); return 1; }
                    }
                }
                if (sink_printf(&sink, ",%G,%G,%G,%G,%G,%G\n",
                                 metrics[mi].fRs,
                                 tineq,
                                 metrics[mi].fBetween,
                                 metrics[mi].fSST,
                                 metrics[mi].fSSE,
                                 metrics[mi].fCHDum) != 0) { fprintf(stderr, "OOM\n"); return 1; }
            }
        }
    }
    if (!write_parquet && !to_stdout) { fclose(out); }

    // If Parquet output requested, convert CSV buffer to Parquet now
    if (write_parquet) {
        if (parquet_write_from_csv_buffer(env_output_parquet, sink.buf ? sink.buf : "", sink.size) != 0) {
            fprintf(stderr, "Failed to write Parquet output\n");
            free(sink.buf);
            return 1;
        }
        free(sink.buf);
    }

    // Free memory
    for (int i = 0; i < rows; ++i) free(rownames[i]);
    for (int j = 0; j < cols; ++j) free(colnames[j]);
    if (raw_values) {
        for (int i = 0; i < rows * cols; ++i) free(raw_values[i]);
        free(raw_values);
    }
    // free coords
    if (coord_samples) {
        for (int i = 0; i < coord_count; ++i) free(coord_samples[i]);
        free(coord_samples);
    }
    free(coord_lats); free(coord_lons);
    free(rownames); free(colnames); free(data); free(Y); free(metrics); free(member1); free(group_means); free(all_member1); free(data_proc); free(lat_values); free(lon_values);

    if (!write_parquet && !to_stdout) { printf("Done. Output written to %s\n", output_path); }
    return 0;
}
