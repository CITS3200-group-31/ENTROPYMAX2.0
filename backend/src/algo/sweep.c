#include "sweep.h"
#include "grouping.h"
#include "metrics.h"

// OWNER: Will
// VB6 mapping: LOOPgroupsizgit brtae → em_sweep_k
int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               const double *Y, double tineq, int32_t k_min, int32_t k_max,
               int32_t *out_opt_k, int32_t perms_n, uint64_t seed,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means,
               int32_t *out_all_member1) {
  if (!data_in || !Y || !out_metrics || rows <= 0 || cols <= 0 || k_min < 1 ||
      k_max < k_min || metrics_cap <= 0) {
    return -1;
  }

  int k, ixout;
  int counter = 0;
  int best_k_index = 0;
  double bineq, rs_stat, ch_stat, sstt, sset, perm_mean, perm_p;
  double best_ch_value = -INFINITY;

  int32_t *member1 = (int32_t *)calloc((unsigned long)rows, sizeof(int32_t));
  int32_t *best_member1 =
      (int32_t *)calloc((unsigned long)rows, sizeof(int32_t));
  double *group_means =
      (double *)calloc((unsigned long)(k_max * cols), sizeof(double));
  double *best_group_means =
      (double *)calloc((unsigned long)(k_max * cols), sizeof(double));
  double *class_table =
      (double *)calloc((unsigned long)(rows * (cols + 1)), sizeof(double));

  if (!member1 || !best_member1 || !group_means || !best_group_means ||
      !class_table) {
    free(member1);
    free(best_member1);
    free(group_means);
    free(best_group_means);
    free(class_table);
    return -1;
  }

  if ((k_max - k_min + 1) > metrics_cap) {
    free(member1);
    free(best_member1);
    free(group_means);
    free(best_group_means);
    free(class_table);
    return -3;
  }

  for (k = k_min; k <= k_max; k++) {
    ixout = 0;

    if (em_initial_groups(rows, k, member1) != 0) {
      continue;
    }

    if (em_switch_groups(data_in, rows, cols, k, tineq, Y, k_min, member1,
                         &bineq, &rs_stat, &ixout, group_means) != 0) {
      continue;
    }

    for (int i = 0; i < rows; i++) {
      class_table[i * (cols + 1)] = (double)member1[i];
      for (int j = 0; j < cols; j++) {
        class_table[i * (cols + 1) + j + 1] = data_in[i * cols + j];
      }
    }

    int ch_result = em_ch_stat(class_table, rows, cols, k, perms_n, seed,
                               &ch_stat, &sstt, &sset, &perm_mean, &perm_p);

    if (ch_result != 0) {
      continue;
    }

    out_metrics[counter].nGrpDum = k;
    // Align naming: store CH in fCHDum and Rs in fRs; retain SST/SSE
    out_metrics[counter].fCHDum = ch_stat;
    out_metrics[counter].fRs = rs_stat;
    out_metrics[counter].fSST = sstt;
    out_metrics[counter].fSSE = sset;
    out_metrics[counter].fBetween = bineq;     // between-region inequality (VB: bineq)
    out_metrics[counter].fCHP = perm_p;
    out_metrics[counter].nCounterIndex = perm_mean;

    double comparison_value = ch_stat;
    if (comparison_value > best_ch_value || (comparison_value == best_ch_value && k < out_metrics[best_k_index].nGrpDum)) {
      best_ch_value = comparison_value;
      best_k_index = counter;
      memcpy(best_member1, member1, (unsigned long)rows * sizeof(int32_t));
      memcpy(best_group_means, group_means,
             (unsigned long)k * (unsigned long)cols * sizeof(double));
    }

    if (out_all_member1) {
      // Store this k's assignments in block [counter * rows .. +rows)
      memcpy(out_all_member1 + (size_t)counter * (size_t)rows, member1, (unsigned long)rows * sizeof(int32_t));
    }
    counter++;
  }

  if (out_opt_k && counter > 0) {
    *out_opt_k = out_metrics[best_k_index].nGrpDum;
  }

  if (out_member1 && counter > 0) {
    memcpy(out_member1, best_member1, (unsigned long)rows * sizeof(int32_t));
  }

  if (out_group_means && counter > 0) {
    int best_k = out_metrics[best_k_index].nGrpDum;
    memcpy(out_group_means, best_group_means,
           (unsigned long)best_k * (unsigned long)cols * sizeof(double));
  }

  free(member1);
  free(best_member1);
  free(group_means);
  free(best_group_means);
  free(class_table);

  return counter;
}

int em_prepare_and_sweep(const double *data_proc, int32_t rows, int32_t cols,
                         int32_t k_min, int32_t k_max,
                         int32_t perms_n, uint64_t seed,
                         em_k_metric_t *out_metrics, int32_t metrics_cap,
                         int32_t *out_member1, double *out_group_means,
                         int32_t *out_all_member1,
                         double *out_tineq) {
  if (!data_proc || rows <= 0 || cols <= 0 || !out_metrics || metrics_cap <= 0) return -1;

  double *Y = (double*)calloc((size_t)cols, sizeof(double));
  if (!Y) return -2;
  double tineq = 0.0;
  if (em_total_inequality(data_proc, rows, cols, Y, &tineq) != 0) { free(Y); return -3; }

  int32_t opt_k = 0;
  int rc = em_sweep_k(data_proc, rows, cols, Y, tineq, k_min, k_max, &opt_k,
                      perms_n, seed, out_metrics, metrics_cap,
                      out_member1, out_group_means, out_all_member1);
  if (out_tineq) *out_tineq = tineq;
  free(Y);
  return rc;
}
