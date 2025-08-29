#include "sweep.h"

#include "logging.h"

// OWNER: Will
// VB6 mapping: LOOPgroupsize → em_sweep_k
int em_sweep_k(const double *data_in, int32_t rows, int32_t cols,
               const double *Y, double tineq, int32_t k_min, int32_t k_max,
               int32_t *out_opt_k, int32_t perms_n, uint64_t seed,
               em_k_metric_t *out_metrics, int32_t metrics_cap,
               int32_t *out_member1, double *out_group_means) {
  if (!data_in || !Y || !out_metrics || rows <= 0 || cols <= 0 || k_min < 1 ||
      k_max < k_min || metrics_cap <= 0) {
    return -1;
  }

  int k, ixout;
  int counter = 0;
  int best_k_index = 0;
  double bineq, rs_stat, ch_stat, sstt, sset, perm_mean, perm_p;
  double best_ch_value = 0.0;

  int32_t *member1 = calloc(rows, sizeof(int32_t));
  int32_t *best_member1 = calloc(rows, sizeof(int32_t));
  double *group_means = calloc(k_max * cols, sizeof(double));
  double *best_group_means = calloc(k_max * cols, sizeof(double));
  double *class_table = calloc(rows * (cols + 1), sizeof(double));

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
    out_metrics[counter].fCHDum = bineq;
    out_metrics[counter].fRs = rs_stat;
    out_metrics[counter].fSST = sstt;
    out_metrics[counter].fSSE = sset;
    out_metrics[counter].fCHF = ch_stat;
    out_metrics[counter].fCHP = perm_p;
    out_metrics[counter].nCounterIndex = perm_mean;

    double comparison_value = ch_stat;
    if (comparison_value > best_ch_value) {
      best_ch_value = comparison_value;
      best_k_index = counter;
      memcpy(best_member1, member1, rows * sizeof(int));
      memcpy(best_group_means, group_means, k * cols * sizeof(double));
    }

    counter++;
  }

  if (out_opt_k && counter > 0) {
    *out_opt_k = out_metrics[best_k_index].nGrpDum;
  }

  if (out_member1 && counter > 0) {
    memcpy(out_member1, best_member1, rows * sizeof(int));
  }

  if (out_group_means && counter > 0) {
    int best_k = out_metrics[best_k_index].nGrpDum;
    memcpy(out_group_means, best_group_means, best_k * cols * sizeof(double));
  }

  free(member1);
  free(best_member1);
  free(group_means);
  free(best_group_means);
  free(class_table);

  return counter;
}
