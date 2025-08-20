#include "grouping.h"
#include <stddef.h>

// OWNER: Will
// VB6 mapping: SetGroups → em_set_groups
int em_set_groups(const double *data, int32_t ng, int32_t rows, int32_t cols,
                  const int32_t *member1, double **fGroupOut)
{
  if (!data || !member1 || !fGroupOut || ng <= 0 || rows <= 0 || cols <= 0)
    return -1;

  int32_t k = 0;
  for (int32_t i = 0; i < ng; i++)
  {
    for (int32_t j = 0; j < rows; j++)
    {
      if (member1[j] == i + 1)
      {
        if (k >= rows)
          return -1;

        fGroupOut[k][0] = i + 1;

        for (int32_t N = 0; N < cols; N++)
        {
          fGroupOut[k][N + 1] = data[j * cols + N];
        }
        k++;
      }
    }
  }
  return 0;
}

// OWNER: Will
// VB6 mapping: INITIALgroup → em_initial_groups
int em_initial_groups(int32_t rows, int32_t k, int32_t *member1)
{
  if (!member1 || rows <= 0 || k <= 0)
    return -1;

  int32_t base = rows / k;
  int32_t extra = rows % k;

  int32_t idx = 0;
  for (int32_t g = 1; g <= k; g++)
  {
    int32_t count = base + (g == k ? extra : 0);
    for (int32_t j = 0; j < count; j++)
    {
      member1[idx++] = g;
    }
  }
  return 0;
}

// OWNER: Will
// VB6 mapping: BETWEENinquality → em_between_inequality
int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1,
                          const double *Y, double *out_bineq)
{
  (void)data;
  (void)rows;
  (void)cols;
  (void)k;
  (void)member1;
  (void)Y;
  (void)out_bineq;
  // TODO [Will]: implement between-group inequality (VB6 BETWEENinquality)
  return -1; // placeholder
}

// OWNER: Will
// VB6 mapping: RSstatistic → em_rs_stat
int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout)
{
  if (!out_rs || !out_ixout)
    return -1;

  if (tineq > 0.0)
  {
    *out_rs = (bineq / tineq) * 100.0;
    *out_ixout = 0;
  }
  else
  {
    *out_rs = 0.0;
    if (bineq == 0.0)
    {
      *out_rs = 100.0;
    }
    *out_ixout = 1;
  }
  return 0;
}

// OWNER: Will (uses Noah's acceptance rule semantics)
// VB6 mapping: SWITCHgroup/OPTIMALgroup → em_optimise_groups
int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double tineq,
                       int32_t *member1, double *out_group_means)
{
  (void)data;
  (void)rows;
  (void)cols;
  (void)k;
  (void)tineq;
  (void)member1;
  (void)out_group_means;
  // TODO [Will]: implement greedy reassignment loop and compute final group means
  //              (VB6 SWITCHgroup and OPTIMALgroup semantics)
  return -1; // placeholder
}
