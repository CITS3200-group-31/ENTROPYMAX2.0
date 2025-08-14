#include "preprocess.h"
#include <math.h>

int em_proportion(double *data, int32_t rows, int32_t cols){
  for(int32_t i=0;i<rows;i++){
    double sum=0.0; for(int32_t j=0;j<cols;j++) sum+=data[i*cols+j];
    if(sum==0.0) continue;
    for(int32_t j=0;j<cols;j++) data[i*cols+j]/=sum;
  }
  return 0;
}

int em_gdtl_percent(double *data, int32_t rows, int32_t cols){
  double grand=0.0; for(int32_t i=0;i<rows;i++) for(int32_t j=0;j<cols;j++) grand+=data[i*cols+j];
  if(grand==0.0) return 0;
  for(int32_t i=0;i<rows;i++) for(int32_t j=0;j<cols;j++) data[i*cols+j]= (data[i*cols+j]/grand)*100.0;
  return 0;
}

int em_means_sd(const double *data, int32_t rows, int32_t cols, double *out_means, double *out_sd){
  for(int32_t j=0;j<cols;j++){ out_means[j]=0.0; out_sd[j]=0.0; }
  for(int32_t i=0;i<rows;i++) for(int32_t j=0;j<cols;j++){ double v=data[i*cols+j]; out_means[j]+=v; out_sd[j]+=v*v; }
  for(int32_t j=0;j<cols;j++){
    out_means[j]/=(double)rows;
    double e2 = out_sd[j]/(double)rows; double m2 = out_means[j]*out_means[j]; double var = e2 - m2;
    if(var < 0.0 && var > -1e-4) var = 0.0;
    out_sd[j] = var<=0.0 ? 0.0 : sqrt(var);
  }
  return 0;
}

