#include "grouping.h"
#include "metrics.h"
#include <math.h>
#include <string.h>

int em_initial_groups(int32_t rows, int32_t k, int32_t *member1){
  int32_t block = rows / k; int32_t upto=0; for(int32_t g=1; g<=k; ++g){
    int32_t target = (g==k)? rows : (upto+block); for(int32_t i=upto;i<target;i++) member1[i]=g; upto=target;
  }
  return 0;
}

int em_between_inequality(const double *data, int32_t rows, int32_t cols,
                          int32_t k, const int32_t *member1,
                          const double *Y, double *out_bineq){
  // Accumulate group sums per variable
  double *yr = (double*)malloc(sizeof(double)*k*cols); if(!yr) return -1; memset(yr,0,sizeof(double)*k*cols);
  int32_t *nr = (int32_t*)malloc(sizeof(int32_t)*k); if(!nr){ free(yr); return -1; } memset(nr,0,sizeof(int32_t)*k);
  for(int32_t i=0;i<rows;i++){
    int32_t g = member1[i]; if(g<1||g>k) continue; int32_t gi=g-1;
    nr[gi]++;
    for(int32_t j=0;j<cols;j++) yr[gi*cols+j] += data[i*cols+j];
  }
  // Normalise by Y
  for(int32_t gi=0;gi<k;gi++) for(int32_t j=0;j<cols;j++) if(Y[j]>0.0) yr[gi*cols+j]/=Y[j];
  // Sum inequality
  double bineq=0.0;
  for(int32_t j=0;j<cols;j++){
    double bineq2=0.0;
    for(int32_t gi=0;gi<k;gi++){
      if(nr[gi]==0) continue; double v = yr[gi*cols+j]; if(v==0.0) continue;
      bineq2 += v * (log(((double)rows * v)/nr[gi]) / log(2.0));
    }
    bineq += Y[j] * bineq2;
  }
  *out_bineq = bineq; free(yr); free(nr); return 0;
}

int em_rs_stat(double tineq, double bineq, double *out_rs, int *out_ixout){
  if(tineq>0.0){ *out_rs = (bineq/tineq)*100.0; *out_ixout = 0; }
  else { *out_rs = (bineq==0.0)? 100.0 : 0.0; *out_ixout = 1; }
  return 0;
}

int em_optimise_groups(const double *data, int32_t rows, int32_t cols,
                       int32_t k, double tineq,
                       int32_t *member1, double *out_group_means){
  // Greedy pass as in SWITCHgroup/OPTIMALgroup
  int stagnant=0;
  while(stagnant<3){
    int changes=0;
    for(int32_t i=0;i<rows;i++){
      int32_t best_g = member1[i]; double best_rs=-1e300; int best_ixout=0; int32_t old = member1[i];
      for(int32_t g=1; g<=k; ++g){
        member1[i]=g; double bineq=0.0; em_between_inequality(data, rows, cols, k, member1, out_group_means /* misused tempor */, &bineq);
        double rs=0.0; int ix=0; em_rs_stat(tineq, bineq, &rs, &ix);
        if(rs>best_rs){ best_rs=rs; best_ixout=ix; best_g=g; }
      }
      member1[i]=best_g; if(best_g!=old) changes++;
    }
    if(changes==0) stagnant++; else stagnant=0;
  }
  // Compute group means
  int32_t *count = (int32_t*)calloc((size_t)k, sizeof(int32_t)); if(!count) return -1;
  memset(out_group_means,0,sizeof(double)*k*cols);
  for(int32_t i=0;i<rows;i++){ int32_t gi=member1[i]-1; count[gi]++; for(int32_t j=0;j<cols;j++) out_group_means[gi*cols+j]+=data[i*cols+j]; }
  for(int32_t gi=0;gi<k;gi++){ if(count[gi]==0) continue; for(int32_t j=0;j<cols;j++) out_group_means[gi*cols+j]/=(double)count[gi]; }
  free(count); return 0;
}

