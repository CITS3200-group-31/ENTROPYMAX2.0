#include "preprocess.h"

// OWNER: Noah
// VB6 mapping: Proportion → em_proportion
int em_proportion(double *data, int32_t rows, int32_t cols){
  (void)data; (void)rows; (void)cols;
  // TODO [Noah]: implement row-wise normalisation (VB6 Proportion)
  return -1; // placeholder
}

// OWNER: Noah
// VB6 mapping: GDTLproportion → em_gdtl_percent
int em_gdtl_percent(double *data, int32_t rows, int32_t cols){
  (void)data; (void)rows; (void)cols;
  // TODO [Noah]: implement grand-total percent normalisation (VB6 GDTLproportion)
  return -1; // placeholder
}

// OWNER: Noah
// VB6 mapping: MeansSTdev → em_means_sd (with negative-variance guard)
int em_means_sd(const double *data, int32_t rows, int32_t cols, double *out_means, double *out_sd){
  (void)data; (void)rows; (void)cols; (void)out_means; (void)out_sd;
  // TODO [Noah]: implement means and SDs (VB6 MeansSTdev)
  return -1; // placeholder
}

