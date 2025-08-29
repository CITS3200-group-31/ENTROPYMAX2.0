#include "grouping.h"

#include <stddef.h>

#include "logging.h"

// OWNER: Will
// VB6 mapping: SetGroups → em_set_groups
int em_set_groups(const double *data, int32_t k, int32_t rows, int32_t cols,
                  const int32_t *member1, double **fGroupOut) {
  if (!data || !member1 || !fGroupOut || k <= 0 || rows <= 0 || cols <= 0) {
    return -1;
  }

  int m = 0;
  for (int i = 0; i < k; i++) {
    for (int j = 0; j < rows; j++) {
      if (member1[j] == i) {
        if (m >= rows) return -1;

        fGroupOut[m][0] = i;

        for (int N = 0; N < cols; N++) {
          fGroupOut[m][N + 1] = data[j * cols + N];
        }
        m++;
      }
    }
  }
  return 0;
}

// OWNER: Will
// VB6 mapping: INITIALgroup → em_initial_groups
int em_initial_groups(int32_t rows, int32_t k, int32_t *member1) {
  if (!member1 || rows <= 0 || k <= 0) {
    return -1;
  }

  int base = rows / k;
  int extra = rows % k;

  int idx = 0;
  for (int g = 0; g <= k; g++) {
    int count = base + (g == (k - 1) ? extra : 0);
    for (int j = 0; j < count; j++) {
      member1[idx++] = g;
    }
  }
  return 0;
}

// OWNER: Will
// VB6 mapping: BETWEENinquality → em_between_inequality
int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1, const double *Y,
                          double *out_bineq) {
  if (!member1 || !data || !Y || !out_bineq || rows <= 0 || cols <= 0 ||
      k <= 0) {
    return -1;
  }

  int group_idx, row_idx;
  int *group_counts = NULL;
  double bineq2;
  double **group_means = NULL;

  group_means = (double **)calloc((size_t)k, sizeof(double *));
  if (!group_means) return -1;

  for (int j = 0; j < k; j++) {
    group_means[j] = (double *)calloc((size_t)cols, sizeof(double));
    if (!group_means[j]) {
      for (int l = 0; l < j; l++) free(group_means[l]);
      free(group_means);
      return -1;
    }
  }

  group_counts = (int *)calloc((size_t)k, sizeof(int));
  if (!group_counts) {
    for (int j = 0; j < k; j++) free(group_means[j]);
    free(group_means);
    return -1;
  }

  for (group_idx = 0; group_idx < k; group_idx++) {
    for (row_idx = 0; row_idx < rows; row_idx++) {
      if (member1[row_idx] != group_idx) continue;

      for (int i = 0; i < cols; i++) {
        group_means[group_idx][i] += data[row_idx * cols + i];
      }
      group_counts[group_idx]++;
    }

    for (row_idx = 0; row_idx < cols; row_idx++) {
      if (Y[row_idx] > 0.0 && group_counts[group_idx] > 0) {
        group_means[group_idx][row_idx] =
            group_means[group_idx][row_idx] / group_counts[group_idx];
      }
    }
  }

  *out_bineq = 0.0;

  for (row_idx = 0; row_idx < cols; row_idx++) {
    bineq2 = 0.0;

    for (group_idx = 0; group_idx < k; group_idx++) {
      if (group_counts[group_idx] == 0 ||
          group_means[group_idx][row_idx] == 0.0) {
        continue;
      }

      double term = group_means[group_idx][row_idx] * (double)rows /
                    (double)group_counts[group_idx];
      bineq2 += group_means[group_idx][row_idx] * log(term) / log(2.0);
    }

    *out_bineq += Y[row_idx] * bineq2;
  }

  for (int j = 0; j < k; j++) {
    free(group_means[j]);
  }
  free(group_means);
  free(group_counts);

  return 0;
}

// OWNER: Will
// VB6 mapping: RSstatistic → em_rs_stat
int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout) {
  if (!out_rs || !out_ixout) {
    return -1;
  }

  if (tineq > 0.0) {
    *out_rs = (bineq / tineq) * 100.0;
    *out_ixout = 0;
  } else {
    *out_rs = 0.0;
    if (bineq == 0.0) {
      *out_rs = 100.0;
    }
    *out_ixout = 1;
  }
  return 0;
}

// OWNER: Will (uses Noah's acceptance rule semantics)
// VB6 mapping: OPTIMALgroup → em_optimise_groups
int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double rs_stat, double *best_stat,
                       int32_t *member1, int32_t current_item,
                       int32_t orig_group, int32_t *iter_count,
                       int32_t min_groups, double *out_group_means) {
  if (!data || !member1 || !out_group_means || rows <= 0 || cols <= 0 ||
      k <= 0) {
    return -1;
  }

  int row, col, current_group;
  int *group_sizes = calloc((size_t)k, sizeof(int));

  if (!group_sizes) {
    return -1;
  }

  if (rs_stat <= *best_stat) {
    (*iter_count)--;
    member1[current_item] = orig_group;
    if (k > min_groups) {
      *best_stat = rs_stat;
      free(group_sizes);
      return 0;
    }
  }

  for (row = 0; row < k; row++) {
    group_sizes[row] = 0;
    for (col = 0; col < cols; col++) {
      out_group_means[row * cols + col] = 0.0;
    }
  }

  for (row = 0; row < rows; row++) {
    current_group = member1[row];
    if (current_group < 0 || current_group >= k) {
      free(group_sizes);
      return -1;
    }

    for (col = 0; col < cols; col++) {
      out_group_means[current_group * cols + col] += data[row * cols + col];
    }
    group_sizes[current_group]++;
  }

  for (row = 0; row < k; row++) {
    if (group_sizes[row] == 0) {
      free(group_sizes);
      return -1;
    }

    for (col = 0; col < cols; col++) {
      out_group_means[row * cols + col] /= group_sizes[row];
    }
  }

  *best_stat = rs_stat;

  free(group_sizes);
  return 0;
}

// OWNER: Will
// VB6 mapping: SWITCHgroup → em_switch_groups
int em_switch_groups(const double *data, int32_t rows, int32_t cols, int32_t k,
                     double tineq, const double *Y, int32_t min_groups,
                     int32_t *member1, double *out_bineq, double *out_rs_stat,
                     int32_t *out_ixout, double *out_group_means) {
  if (!data || !member1 || !out_group_means || rows <= 0 || cols <= 0 ||
      k <= 0) {
    return -1;
  }

  // int32_t calculation_count = 0;
  // Tracks how many different group assignment combinations have been evaluated
  // during the optimization process.
  int restart_count = 0;
  int improvements_found;
  double best_stat = 0.0;

  do {
    improvements_found = 0;

    for (int sample = 0; sample < rows; sample++) {
      for (int target_group = 0; target_group < k; target_group++) {
        int original_group = member1[sample];
        member1[sample] = target_group;
        // calculation_count++;

        em_between_inequality(data, rows, cols, k, member1, Y, out_bineq);

        em_rs_stat(tineq, *out_bineq, out_rs_stat, out_ixout);

        int iter_count = 0;
        em_optimise_groups(data, rows, cols, k, *out_rs_stat, &best_stat,
                           member1, sample, original_group, &iter_count,
                           min_groups, out_group_means);

        if (iter_count > 0) improvements_found++;
      }
    }

    if (improvements_found == 0) {
      restart_count++;
    }

  } while (restart_count < 3);

  // VB original: If intmed = 1 Then Call BESTgroup(statmx, ng, jobs, member1())
  // Omitted - pure logging function, no computational impact

  return 0;
}
