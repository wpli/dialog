/*

Main code for wrapping matlab's matrices in something else.

$Id: mxInfo.c,v 1.15 2007-09-07 13:39:53 jdrf Exp $



Copyright 2006-     by Jason D.R. Farquhar (jdrf@zepler.org)
Permission is granted for anyone to copy, use, or modify this
software and accompanying documents for any uncommercial
purposes, provided this copyright notice is retained, and note is
made of any changes that have been made. This software and
documents are distributed without any warranty, express or
implied


*/

#include "mxInfo.h"

/*-------------------------------------------------------------------------*/
/* struct to hold useful info for iterating over a n-d matrix              */
/* e.g. for 3 x 3 x 3 matrix:
   ndim=3, numel=27, sz=[2 2 2], stride=[1 3 9] */
/* MATLAB specific helper function */
#ifdef MATLAB_MEX_FILE
MxInfo mkmxInfo(const mxArray *mat, int nd){
  MxInfo minfo;
  int i;
  int rnd = mxGetNumberOfDimensions(mat);
  const int *dim = mxGetDimensions(mat);
  int dtype = mxGetClassID(mat);   
  if( !(dtype == DOUBLE_DTYPE || dtype==SINGLE_DTYPE || dtype==INT32_DTYPE) )
	 mexErrMsgTxt("Only defined for double/single/int32 matrices -- sorry!");
  minfo.dtype = dtype;
  if ( nd==0 ) nd=rnd; /* 0 indicates default dim size */
  if ( nd==0 ) nd=1;   /* always at least 1 dim */
  minfo.nd = nd;
  /* use a single malloc call to get all the mem we need */
  minfo.sz     = (int *)MALLOC(sizeof(int)*(minfo.nd*2+1));
  minfo.stride = minfo.sz+minfo.nd;
  minfo.numel     = 1;
  minfo.stride[0] = 1; 
  for (i = 0; i < minfo.nd; i++) {  /* copy dims to get result size */
	 minfo.sz[i]= (i<rnd) ? dim[i] : 1;/* comp the max idx, 1 pad extras */
	 /* compute the x/y strides for this dim */
	 minfo.stride[i+1] = minfo.stride[i]*minfo.sz[i]; /* nd+1 strides */
	 minfo.numel  *= minfo.sz[i]; /* total matrix size */
  }
  minfo.rp = mxGetPr(mat);
  if ( mxIsComplex(mat) ) minfo.ip = mxGetPi(mat); else minfo.ip=0;
  return minfo;
}

mxArray* mkmxArray(const MxInfo info){
  mxArray *mx = 
	 mxCreateNumericMatrix(0,0,info.dtype,(info.ip==0)?mxREAL:mxCOMPLEX);
  /* only valid if strides are consistent with single matrix */
  if ( !isContiguous(info) ) 
	 mexErrMsgTxt("Can't make mxarray from this mxInfo -- no uniform memory");
  
  mxSetDimensions(mx,info.sz,info.nd);
  mxSetPr(mx,info.rp); mxSetPi(mx,info.ip);
  return mx;
  
}

mxArray* mkmxArrayCopy(const MxInfo info){
  mxArray *mx = mxCreateNumericArray(info.nd,info.sz,info.dtype,
												 (info.ip==0)?mxREAL:mxCOMPLEX);
  mxSetDimensions(mx,info.sz,info.nd);
  copyData(info,info.rp,mxGetPr(mx));
  if ( info.ip ) copyData(info,info.ip,mxGetPi(mx));
  return mx;
}

#else /* C helper functions */

MxInfo mkmxInfo(int nd, const int *dim, double *rp, double *ip, MxInfoDTypes dtype){
  MxInfo minfo;
  int i;
  if( !(dtype == DOUBLE_DTYPE || dtype==SINGLE_DTYPE || dtype==INT32_DTYPE) ){
	 ERROR("Only defined for double/single/int32 matrices -- sorry!");
  }
  minfo.dtype = dtype;
  if ( nd==0 ) nd=1;   /* always at least 1 dim */
  minfo.nd = nd;
  /* use a single malloc call to get all the mem we need */
  minfo.sz     = (int *)MALLOC(sizeof(int)*(minfo.nd*2+1));
  minfo.stride = minfo.sz+minfo.nd;
  minfo.numel     = 1;
  minfo.stride[0] = 1; 
  for (i = 0; i < minfo.nd; i++) {  /* copy dims to get result size */
	 minfo.sz[i]= (i<nd) ? dim[i] : 1;/* comp the max idx, 1 pad extras */
	 /* compute the x/y strides for this dim */
	 minfo.stride[i+1] = minfo.stride[i]*minfo.sz[i]; /* nd+1 strides */
	 minfo.numel  *= minfo.sz[i]; /* total matrix size */
  }
  minfo.rp = rp;
  minfo.ip = ip; 
  return minfo;
}

void printMxInfo(FILE* fd, const MxInfo info){
  fprintf(fd,"[");
  int i,j,idx;
  for ( i=0; i < info.nd-1; i++ ) { fprintf(fd,"% d x",info.sz[i]); }
  fprintf(fd," %d",info.sz[i]);
  fprintf(fd," ]");
  if ( info.dtype==SINGLE_DTYPE ) fprintf(fd," (single"); else fprintf(fd," (double");
  if ( info.ip==0 ) fprintf(fd,")"); else fprintf(fd," complex)");

  fprintf(fd,"\n");
  int nCol = (info.nd>1?info.sz[1]:1);
  for ( i=0; i < nCol; i++){
	 for ( j=0; j < info.sz[0]; j++){
		idx = i*info.stride[1]+j*info.stride[0];
		if( info.dtype==DOUBLE_DTYPE ) { 
		  fprintf(fd,"%lf ",info.rp[idx]); 
		} else {                         
		  fprintf(fd,"%f ",(((float*)info.rp)[idx]));  
		}
		if ( info.ip!=0 ) {
		  if( info.dtype==DOUBLE_DTYPE ) { 
			 fprintf(fd,"+ i %lf ",info.ip[idx]); 
		  } else {                         
			 fprintf(fd,"+ i %f ",(((float*)info.ip)[idx])); 
		  }
		}
	 }
	 fprintf(fd,"\n");
  }
}

#endif /* MATLAB/C helper functions */

MxInfo mkemptymxInfo(int nd){
  MxInfo minfo;
  nd = (nd==0)?1:nd; /* always at least 1 dim */
  minfo.nd = nd;
  minfo.numel=0;
  /* use a single malloc call to get all the mem we need */
  minfo.sz     = (int *)CALLOC(nd*2+1,sizeof(int));
  minfo.stride = minfo.sz+nd;
  minfo.rp = 0;
  minfo.ip = 0; 
  minfo.dtype = DOUBLE_DTYPE;
  return minfo;
}

MxInfo copymxInfo(const MxInfo inf){
  MxInfo minfo;
  int i;
  minfo.nd = inf.nd;
  minfo.numel=inf.numel;
  /* use a single malloc call to get all the mem we need */
  minfo.sz     = (int *)CALLOC(inf.nd*2+1,sizeof(int));
  minfo.stride = minfo.sz+inf.nd;
  for(i=0;i<inf.nd;i++){ 
	 minfo.sz[i]=inf.sz[i]; 
	 minfo.stride[i]=inf.stride[i];
  }
  minfo.stride[i]=inf.stride[i]; /* nd+1 valid strides */
  minfo.rp = inf.rp;
  minfo.ip = inf.ip; 
  minfo.dtype = inf.dtype;
  return minfo;
}

void delmxInfo(MxInfo *minfo) {
  FREE(minfo->sz);
}

/* compute if the input info array is contiguous in memory */
char isContiguous(const MxInfo info){
  int d;
  for(d=0; d<info.nd; d++) 
	 if ( info.stride[d+1] != info.stride[d]*info.sz[d] ) break; 
  return info.stride[0]==1 && d==info.nd;
}

/* inlined away ! --- or not because of silly MACS */
int sz(const MxInfo info,int i){
  return (i<info.nd)?info.sz[i]:1;
}
int stride(const MxInfo info, int i){
  return (i<info.nd+1)?info.stride[i]:info.stride[info.nd];
}

int dsz_bytes(const MxInfo info){
  int dsz=0;
  switch( info.dtype ){
  case LOGICAL_DTYPE: dsz=1; break;
  case CHAR_DTYPE   : dsz=1; break;
  case DOUBLE_DTYPE : dsz=sizeof(double); break;
  case SINGLE_DTYPE : dsz=sizeof(float); break;
 /*  case INT8_DTYPE   : dsz=1; */
  case UINT8_DTYPE  : dsz=1; break;
  case INT16_DTYPE  : dsz=2; break;
  case UINT16_DTYPE : dsz=2; break;
  case INT32_DTYPE  : dsz=4; break;
  case UINT32_DTYPE : dsz=4; break;
  case INT64_DTYPE  : dsz=8; break;
  case UINT64_DTYPE : dsz=8; break;
  }
  return dsz;
}

void copyData(const MxInfo info, const double *from, double *to){
  /* copy the real part */
  const char *xp=(char*)from;
  char *zp=(char *)to;
  int dsz=dsz_bytes(info);
  const char *zendp=(char *)zp+(info.numel)*dsz;
  if ( isContiguous(info) ){ /* simple linear copy */
	 while ( zp < zendp ) *zp++ = *xp++;
  } else {
	 int i;
	 int *subs =(int*)CALLOC(info.nd,sizeof(int));
	 while ( zp < zendp ) {
		for( i=0; i < dsz; i++ ) zp[i] = xp[i];
		zp += dsz;
		for( i=0; i < info.nd; i++ ){
		  /* if reached the last element of this dim */
		  xp += info.stride[i]*dsz; 
		  subs[i]++;        /* move on to the next element */
		  if( subs[i] < info.sz[i] ){/*move this dim on by one and stop!*/
			 break;
		  } else {
			 subs[i] = 0; /* reset to the start again! */
			 xp -= info.stride[i]*info.sz[i]*dsz; 
		  } 
		}
	 }
	 FREE(subs);
  }
}


