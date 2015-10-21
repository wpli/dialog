/*

tprod_mex.c

Generalised multiply accumulate operation. == tensor product with repeated
indicies

N.B. compile with TPRODLIB defined to get an version without mexFunction
defined to use in other mex-files
  
$Id: tprod_mex.c,v 1.10 2007-09-07 13:56:13 jdrf Exp $

*/

#include "mex.h"
#include "matrix.h"
#include "mxInfo.h"
#include "tprod.h"

#ifndef MAX
#define MAX(A,B)  ((A) > (B) ? (A) : (B))
#define MIN(A,B)  ((A) < (B) ? (A) : (B))
#endif

/* matlab call to do the matrix product when possible */
mxArray* MATLAB_mm(MxInfo zinfo, const MxInfo xinfo, const MxInfo yinfo,
						 const MxInfo xrest, const MxInfo yrest,
						 const MxInfo xmaccinfo, const MxInfo ymaccinfo);

/* size at which it becomes more efficient to use tprod code than calling
	back to matlab */
const int MATLABMACCTHRESHOLDSIZE=201;
const int DEFAULTBLKSZ=32;

/*
  This function computes the generalised matrix products.  Basicially it
  works by spliting the input X and Y matrices into 2 *virtual* sub-matrices,
  one for the "outer" product dimensions (x/y rest) (over which the cartesian
  product is computed) and one for the "inner" product matrices (over which
  the inner product - or multiply accumulate - is computed).  Once these 2
  matrices have been computed the result is simply an outer product in
  tprod and inner product in macc */
void mexFunction(const int nlhs, mxArray *plhs[], 
                 const int nrhs, const mxArray *prhs[]) {
  char msgTxt[256];
  int i, j, maccnd=0, seqnd=0, BLKSZ=DEFAULTBLKSZ, indtype, retVal;
  const int xarg=0, ydimspecarg=3;
  int xdimspecarg=0, yarg=0; /* possibly other way round? */
  bool useMATLAB=true;
  int callType=0;
  MxInfo xinfo, yinfo, zinfo;
  MxInfo xmacc, ymacc, zrest, xrest, yrest;
  int znd, xnidx=0, ynidx=0;
  int *x2yIdx=0;
  if (nrhs < 4 || nrhs >6)	 ERROR("tprod: Incorrect number of inputs.");
  if (nlhs > 1)	 ERROR("tprod: Too many output arguments.");
  if ( mxGetNumberOfDimensions(prhs[ydimspecarg]) > 2 )
	 ERROR("tprod: ydimspec must be a vector");
  /* parse the tprod options list */
  if( nrhs >= 5 && mxIsChar(prhs[4]) ) {
	 char *opnmStr=mxArrayToString(prhs[4]);
	 for (i=0 ; opnmStr[i] != 0; i++ ) {
		switch ( opnmStr[i] ) {
		case 'm': case 'M':   useMATLAB=false;  break;
		case 'n': case 'N':   callType=1;    break; /* new call type */
		case 'o': case 'O':   callType=-1;   break; /* old call type */
		default: 
		  WARNING("tprod: Unrecognised tprod option");
		}
	 }
	 mxFree(opnmStr); opnmStr=0;
  }

  if ( nrhs==6 && mxGetNumberOfElements(prhs[5])==1 ){
	 BLKSZ=(int)mxGetScalar(prhs[5]);
  }

  /* Get X */
  xinfo = mkmxInfo(prhs[xarg],0);
  /* remove trailing singlenton dimensions from x and y */
  for( i=xinfo.nd; i>1; i-- ) if ( xinfo.sz[i-1]!=1 ) break;  xinfo.nd=i;

  /*----------------------------------------------------------------------*/
  /* Identify the calling convention used */
  if ( callType == 0 ) {

	 /* Try and identify the calling convention used, i.e. 
		 X,Y,xdimspec,ydimspec, or X,xdimspec,Y,ydimspec (deprecated) */
	 if ( mxGetNumberOfDimensions(prhs[1])==2 &&		
			( (mxGetN(prhs[1])==1 && mxGetM(prhs[1])>=xinfo.nd) /* Xdimspec OK */
			  || (mxGetN(prhs[1])>=xinfo.nd && mxGetM(prhs[1])==1) ) ) {
		yarg  = 2; /* start by trying new call type */
		int ynd = mxGetNumberOfDimensions(prhs[yarg]);
		const int *ysz = mxGetDimensions(prhs[yarg]); /* size of poss Y*/
		for( i=ynd; i>1; i-- ) if ( ysz[i-1]!=1 ) break; ynd=i; 
		if( mxGetNumberOfElements(prhs[ydimspecarg]) >= ynd ){/*Ydimspec OK*/
		  callType = 1 ;  /* new call type */
		}
	 }
	 if( mxGetNumberOfDimensions(prhs[2])==2 &&
		  ((mxGetN(prhs[2])==1 && mxGetM(prhs[2])>=xinfo.nd)/* xdimspec OK */
			|| (mxGetN(prhs[2])>=xinfo.nd && mxGetM(prhs[2])==1) ) ) {
		/* Consitent so far, check the ydimspec is OK */
		yarg  = 1; /* start by trying new call type */
		int ynd = mxGetNumberOfDimensions(prhs[yarg]);
		const int *ysz = mxGetDimensions(prhs[yarg]); /* size of poss Y*/
		for( i=ynd; i>1; i-- ) if ( ysz[i-1]!=1 ) break; ynd=i; 
		if ( mxGetNumberOfElements(prhs[ydimspecarg]) >= ynd ) {
		  
		  if ( callType == 0 ) { /* argument 3 is CONSISTENT, and 2 *WASN'T* */
			 callType = -1; 
			 
		  } else { /* argument 2 consistent ALSO */
			 /* of one of them matches exactly and the other doesn't */
			 int xnd = mxGetNumberOfDimensions(prhs[xarg]); /* num input X dims */
			 if ( xnd==2 && xinfo.nd == 1 ) xnd=1; /* col vec is special case*/
			 if ( xnd == mxGetNumberOfElements(prhs[1]) /* 1 matches *exactly* */
					&& xnd != mxGetNumberOfElements(prhs[2]) ) { /* 2 doesn't */
				callType = 1;
			 } else if( xnd == mxGetNumberOfElements(prhs[2])/* 2 *exact* match */
							&& xnd != mxGetNumberOfElements(prhs[1]) ){/* 1 doesn't */
				callType = -1;
			 } else { /* neither or both match exactly */
				callType = 1;
				WARNING("tprod: Could not unambigiously determine calling convention, tprod(X,xdimspec,Y,ydimspec) assumed. Use 'n' or 'o' to force new/old convention.");
			 }
		  }
		}
	 } 
  }
  switch ( callType ) {
  case 1:  xdimspecarg=1; yarg=2; break;/* new type: X,xdimspec,Y,xdimspec */
  case -1: xdimspecarg=2; yarg=1; break;/* old type: X,Y,xdimspec,xdimspec */
  default: ERROR("tprod: Couldnt identify calling convention.");
  }

  /* Now we know where the Y is we can get it too! */
  yinfo = mkmxInfo(prhs[yarg],0); 
  /* empty set as input for y means make it copy of x */
  if ( yinfo.numel==0 && yinfo.nd==2 && yinfo.sz[0]==0 && yinfo.sz[1]==0 ) { 
	 yinfo=copymxInfo(xinfo); 
  }
  /* remove trailing singlenton dimensions from x and y */
  for( i=yinfo.nd; i>1; i-- ) if ( yinfo.sz[i-1]!=1 ) break;  yinfo.nd=i;

  /* check the types are what we can use */
  if ( !(xinfo.dtype == DOUBLE_DTYPE || xinfo.dtype == SINGLE_DTYPE ) ){
	 ERROR("tprod: X type unsuppored: only double, single");
  }
  if ( !(yinfo.dtype == DOUBLE_DTYPE || yinfo.dtype == SINGLE_DTYPE ) ){
	 ERROR("tprod: Y type unsuppored: only double, single");
  }
     
  /*-------------------------------------------------------------------------
   * Initialise x2yIdx which maps from input dimensions to the type of output
	* we want.  The format of x2yIdx is:
	*   [Xdimlabels Ydimlabels] 
	* so it reflects the order of the dimensions in the output Z.
   * The value and sign of the integer label tells us what type of
   * operation to perform on this dimension.
	*    0   this is a squeezed dim which must be singlenton
	*   -ve  this is the index in X/Y of the matching dim to be accumulated
	*   +ve  this number is the position of the dimension at this location in
   *        the output matrix.
	*-------------------------------------------------------------------------*/
  znd=0; /* xnidx, ynidx; */
  double *xip, *yip;
  /* fill in the x2yIdx for the new type of indicies */
  maccnd=0;
  xnidx=mxGetNumberOfElements(prhs[xdimspecarg]);
  if( xnidx<xinfo.nd ) ERROR("tprod:Less X indicies than dimensions");
  ynidx=mxGetNumberOfElements(prhs[ydimspecarg]);
  if( ynidx<yinfo.nd ) ERROR("tprod:Less Y indicies than dimensions");

  x2yIdx=(int*)mxCalloc(xnidx+ynidx,sizeof(int));  	 
  xip=mxGetPr(prhs[xdimspecarg]); yip=mxGetPr(prhs[ydimspecarg]);

  /* find the max value of xip, this is num output dims */
  /* also check for non multiple instances of acc dims labels */
  znd=MAX((int)xip[0],0);
  for( i=1; i<xnidx; i++){
	 if ( xip[i] < .0 ) {
		for( j=0; j<i; j++)
		  if(xip[i]==xip[j]) ERROR("tprod: Duplicate x-dim label");
	 } else if ( xip[i] > .0 ) {
		znd=MAX(znd,(int)xip[i]); /* find the largest target dim */
	 } else if ( sz(xinfo,i)!=1 ) 
		ERROR("tprod: Ignored dims *MUST* have size 1");
  }
  /* same for yip */
  /* but also check that we always have matching x label to accumulate */
  znd=MAX(znd,(int)yip[0]); 
  for( i=1; i<ynidx; i++){
	 if ( yip[i] < .0 ) {
		for( j=0; j<i; j++)
		  if(yip[i]==yip[j]) ERROR("tprod: Duplicate y-dim label");
		for( j=0; j<xnidx; j++) if( yip[i]==xip[j] ) break;
		if( j==xnidx ) {
		  sprintf(msgTxt,"tprod: Couldn't find a matching negative x-label for the y-label=%d",(int)yip[i]);
		  ERROR(msgTxt);
		}
	 } else if ( yip[i] > .0 ) {
		znd=MAX(znd,(int)yip[i]); /* find the largest target dim */
	 } else if ( sz(yinfo,i)!=1 ) 
		ERROR("tprod: Ignored dims *MUST* have size 1");
  }

  /* compute the x->y mapping */
  for( i=0; i<xnidx; i++){
	 if ( xip[i] < .0 ) {
		/* search for the matching y */
		for( j=0; j<ynidx; j++) {
		  if ( yip[j]==xip[i] ) {
			 x2yIdx[i]=-(j+1);    x2yIdx[xnidx+j]=-(i+1);    maccnd++;
			 break;
		  }
		}
		if ( x2yIdx[i]==0 )
		  ERROR("tprod: Couldn't find a matching y-idx for the x");
		if( sz(xinfo,i) != sz(yinfo,j)) /* check sizes match too */
		  ERROR("tprod: Matched dims must have the same size!");
	 } else { /* just copy it through */
		x2yIdx[i]=(int)xip[i];
		/* search for the matching y, & check sizes match */
		for( j=0; j<ynidx && yip[j]!=xip[i]; j++);
		if ( j<ynidx ){ /* sequential dimension */
		  if ( sz(xinfo,i) != sz(yinfo,j) )
			 ERROR("tprod: Matched dims must have the same size!");
		  if ( sz(xinfo,i)!=1 ) { /* only *really* sequ if >1 size strides */
			 seqnd++; 
		  } 
		}
	 }
  }
  /* now set the y parts -- for the non-set non-accumulated dimensions */ 
  for( i=0; i<ynidx; i++){ 
	 if( yip[i] > .0 ) { x2yIdx[i+xnidx]=(int)yip[i]; }
  }
  /*   } */
  znd=MAX(znd,1); /* ensure at least 1 output dim */
  maccnd=MAX(maccnd,1); /* ensure at least 1 macc dim */
  
  /* compute the mxInfo for the accumulated and rest sub-matrices */  
  xmacc = mkemptymxInfo(maccnd);
  ymacc = mkemptymxInfo(maccnd);
  /* N.B. xrest.sz holds the	size of the combined x and y rest matrix */
  xrest = mkemptymxInfo(znd); 
  yrest = mkemptymxInfo(znd);

  initrestmaccmxInfo(znd, xinfo, yinfo, x2yIdx, xnidx, ynidx,
							&xrest, &yrest, &xmacc, &ymacc);

  /* compute the size of the output matrix */
  zinfo=initzmxInfo(znd, xinfo, yinfo, x2yIdx, xnidx, ynidx); 

  /* optimise/standardize the query so its the way tprod wants it */
  zrest = copymxInfo(zinfo);
  optimisetprodQuery(&zrest, &xrest, &yrest, &xmacc, &ymacc);  
  if ( xrest.rp != xinfo.rp ) { /* swap xinfo/yinfo if needed */
	 MxInfo tmp = xinfo; xinfo=yinfo; yinfo=tmp;
  }

  /* Now do the actuall work to compute the result */  
  if ( yinfo.numel==0 || xinfo.numel== 0 ) { /* deal with null inputs */
	 WARNING("tprod: Empty matrix input!");
	 /* return an empty matrix */
	 plhs[0]=mxCreateNumericArray(zinfo.nd,zinfo.sz,mxDOUBLE_CLASS,
											(xinfo.ip==0&&yinfo.ip==0)?mxREAL:mxCOMPLEX);
	 	 
  } else if ( useMATLAB && /* allowed */
		 seqnd==0 &&                     /* no sequential dims */
		 xmacc.nd <= 1 &&            /* at most 1 macc dim */
		 xrest.nd <= 2 &&            /* at most 2 output dims */
		 (xrest.nd<= 1 ||            /* 1 from X */
		  ((xrest.stride[0]==0) || (stride(xrest,1)==0))) && 
 		 (yrest.nd<= 1 ||            /* 1 from Y */
		  ((yrest.stride[0]==0) || (stride(yrest,1)==0))) &&
				  (xmacc.numel*(2+(xinfo.ip==0)+(yinfo.ip==0)) < MATLABMACCTHRESHOLDSIZE ) /* not tooo big! */
				  ){ 
	 /* Phew! we can use matlab! */
	 if ( xrest.stride[0]>0 ) { /* x comes before y in output */
		plhs[0]=MATLAB_mm(zinfo,xinfo,yinfo,xrest,yrest,
								xmacc,ymacc);
	 } else { /* y comes before x in output, reverse order of inputs */
		plhs[0]=MATLAB_mm(zinfo,yinfo,xinfo,yrest,xrest,
								ymacc,xmacc);
	 }
  } else {

	 /* otherwise do it ourselves */
	 /* create the data for the z matrix and set its pointer */
	 plhs[0]=mxCreateNumericArray(zinfo.nd,zinfo.sz,zinfo.dtype,
											(xinfo.ip==0&&yinfo.ip==0)?mxREAL:mxCOMPLEX);
	 zinfo.rp = mxGetPr(plhs[0]); zrest.rp=zinfo.rp;
	 zinfo.ip = mxGetPi(plhs[0]); zrest.ip=zinfo.ip;

	 /* call tprod to do the real work */
	 /* do the (appropriately typed) operation */
	 if(        xrest.dtype==DOUBLE_DTYPE && yrest.dtype==DOUBLE_DTYPE ) {/*dd*/
		retVal= ddtprod(zrest,xrest,yrest,xmacc,ymacc,BLKSZ);

	 } else if( xrest.dtype==DOUBLE_DTYPE && yrest.dtype==SINGLE_DTYPE ) {/*ds*/
		retVal= dstprod(zrest,xrest,yrest,xmacc,ymacc,BLKSZ);

	 } else if( xrest.dtype==SINGLE_DTYPE && yrest.dtype==DOUBLE_DTYPE ) {/*sd*/
		retVal= sdtprod(zrest,xrest,yrest,xmacc,ymacc,BLKSZ);
 
	 } else if( xrest.dtype==SINGLE_DTYPE && yrest.dtype==SINGLE_DTYPE ){/*ss*/
		retVal= sstprod(zrest,xrest,yrest,xmacc,ymacc,BLKSZ);

	 } else {
 		ERROR("tprod: Inputs of unsupported type: only double/single");
		
	 }
	 /* check for errors */
	 switch ( retVal ) {
	 case ZTYPEMISMATCH : 
		ERROR("tprod: Z is of unsupported type"); break;
	 case XTYPEMISMATCH :
		ERROR("tprod: X is of unsupported type"); break;
	 case YTYPEMISMATCH :
		ERROR("tprod: Y is of unsupported type"); break;
	 case INTYPEMISMATCH :
		ERROR("tprod: input real/complex mix unsupported"); break;
	 case OTHERERROR :
		ERROR("tprod: Something else went wrong, sorry!"); break;
	 default: ;
	 }
  }
  
  /* ensure the output has the size we want */
  if ( plhs[0] ) mxSetDimensions(plhs[0],zinfo.sz,zinfo.nd);
  
  /* free up all the memory we've allocated */
  /* N.B. not clear we need to do this from the matlab web-site should happen
	  automatically */
  delmxInfo(&xinfo);delmxInfo(&yinfo);delmxInfo(&zinfo);
  delmxInfo(&xmacc);  delmxInfo(&ymacc);
  delmxInfo(&xrest);  delmxInfo(&yrest);
  FREE(x2yIdx);
}

/*-------------------------------------------------------------------------*/
/* the input problem could be reduced to a conventional 2D matrix product..
	so here we use the fast MATLAB version */
mxArray* MATLAB_mm(MxInfo zinfo, const MxInfo xinfo, const MxInfo yinfo,
						 const MxInfo xrest, const MxInfo yrest,
						 const MxInfo xmacc, const MxInfo ymacc){
  mxArray *Xmx, *Ymx, *Zmx, *args[2];
  /* call matlab to do the real work -- more reliable than dgemm */
  /* first create a new matrix with the right size to use in the matlab call*/
  /* create and empty array */
  Xmx= mxCreateNumericMatrix(0,0,xinfo.dtype,(xinfo.ip==0)?mxREAL:mxCOMPLEX);
  Ymx= mxCreateNumericMatrix(0,0,yinfo.dtype,(yinfo.ip==0)?mxREAL:mxCOMPLEX);
  /* and populate it with data */
  mxSetPr(Xmx,xinfo.rp); if ( xinfo.ip ) mxSetPi(Xmx,xinfo.ip);
  mxSetPr(Ymx,yinfo.rp); if ( yinfo.ip ) mxSetPi(Ymx,yinfo.ip);

  /* Set trap so errors return here so we can clean up correctly */
  mexSetTrapFlag(1);

  /* now do the calls to matlab to get the result */
  args[0] = Xmx; args[1]= Ymx;
  Zmx=0;  
  /* no accumulated dims -- just outer product, or just inner product */
  if ( xmacc.nd == 1 && xmacc.sz[0]==1 ) { 
	 /* set X as its vector version, implicitly transpose Y and then prod */
	 mxSetM(Xmx,MAX(sz(xrest,0),1)); mxSetN(Xmx,1);
	 mxSetM(Ymx,1);                  mxSetN(Ymx,MAX(sz(yrest,1),1)); 
	 mexCallMATLAB(1, &Zmx, 2, args, "*");

  } else if ( xmacc.stride[0] == 1 && ymacc.stride[0] == 1 ){ 
	 /* | x | == macc/rest * macc/rest*/
	 mxSetM(Xmx,xmacc.sz[0]);     mxSetN(Xmx,xinfo.numel/xmacc.sz[0]);
	 mxSetM(Ymx,ymacc.sz[0]);     mxSetN(Ymx,yinfo.numel/ymacc.sz[0]);
	 
	 /* transpose X and call matlab */
	 if( yinfo.numel+zinfo.numel>xinfo.numel*.75 ){/*cheaper to transpose X*/
		mxArray *XmxT;
		mexCallMATLAB(1, &XmxT, 1, &Xmx, ".\'");/* N.B. this copies X!!! */
		args[0]=XmxT;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mxDestroyArray(XmxT);

	 } else { /*cheaper to transpose y and z */
		mxArray *YmxT;
		mexCallMATLAB(1, &YmxT, 1, &Ymx, ".\'");/* N.B. this copies Y!!! */
		args[0]=YmxT; args[1]=Xmx;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mxDestroyArray(YmxT);
		if( ymacc.sz[0]!=yinfo.numel ) {/* transpose result if necessary */
		  mxArray *ZmxT;
		  mexCallMATLAB(1, &ZmxT, 1, &Zmx, ".\'");/* N.B. this copies Z!!! */
		  mxDestroyArray(Zmx);
		  Zmx=ZmxT;		
		}
	 }
  } else if ( xmacc.stride[0] == 1 && ymacc.stride[0] > 1 ){
	 /* | x _ == macc/rest * rest/macc */
	 mxSetM(Xmx,xmacc.sz[0]);      
	 mxSetN(Xmx,xinfo.numel/xmacc.sz[0]);
	 mxSetM(Ymx,ymacc.stride[0]);  
	 mxSetN(Ymx,yinfo.numel/ymacc.stride[0]);	 

	 if( yinfo.numel+xinfo.numel<zinfo.numel*.75 ){/* cheaper to transpose Z */
		/* reverse order of multiply, call matlab and transpose Z */	 
		mxArray *ZmxT;
		args[0]=Ymx; args[1]=Xmx;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mexCallMATLAB(1, &ZmxT, 1, &Zmx, ".\'");/* N.B. this copies Z!!! */
		mxDestroyArray(Zmx);
		Zmx=ZmxT;

	 } else { /* cheaper to transpose twice */
		mxArray *XmxT, *YmxT;
		mexCallMATLAB(1, &XmxT, 1, &Xmx, ".\'");/* N.B. this copies X!!! */
		mexCallMATLAB(1, &YmxT, 1, &Ymx, ".\'");/* N.B. this copies Y!!! */
		args[0]=XmxT; args[1]=YmxT;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mxDestroyArray(XmxT); mxDestroyArray(YmxT);
	 }
	 
  } else if ( xmacc.stride[0] >  1 && ymacc.stride[0] == 1 ){
	 /* _ x | == rest/macc * macc/rest */
	 mxSetM(Xmx,xmacc.stride[0]); 
	 mxSetN(Xmx,xinfo.numel/xmacc.stride[0]);
	 mxSetM(Ymx,ymacc.sz[0]);     
	 mxSetN(Ymx,yinfo.numel/ymacc.sz[0]); 
	 mexCallMATLAB(1, &Zmx, 2, args, "*");

  } else if ( xmacc.stride[0] > 1 && ymacc.stride[0] > 1 ){
	 /* _ x _ == rest/macc * rest/macc */ 
	 mxSetM(Xmx,xmacc.stride[0]);  
	 mxSetN(Xmx,xinfo.numel/xmacc.stride[0]);
	 mxSetM(Ymx,ymacc.stride[0]);  
	 mxSetN(Ymx,yinfo.numel/ymacc.stride[0]);	 

	 if( xinfo.numel+zinfo.numel>yinfo.numel*.75 ){/* cheaper to transpose Y */
		/* transpose Y and call matlab */
		mxArray *YmxT;
		mexCallMATLAB(1, &YmxT, 1, &Ymx, ".\'");/* N.B. this copies Y!!! */
		args[1]=YmxT;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mxDestroyArray(YmxT);

	 } else { /* cheaper to transpose X and Z */
		mxArray *XmxT;
		mexCallMATLAB(1, &XmxT, 1, &Xmx, ".\'");/* N.B. this copies X!!! */
		args[0]=Ymx; args[1]=XmxT;
		mexCallMATLAB(1, &Zmx, 2, args, "*");
		mxDestroyArray(XmxT);
		if( xmacc.sz[0]!=xinfo.numel ) {/* transpose result if necessary */
		  mxArray *ZmxT;
		  mexCallMATLAB(1, &ZmxT, 1, &Zmx, ".\'");/* N.B. this copies Z!!! */
		  mxDestroyArray(Zmx);
		  Zmx=ZmxT;		
		}
		
	 }

  } else {
	 ERROR("tprod: somethings gone horibbly wrong!");
  }

  /* Set trap so errors return here so we can clean up correctly */
  mexSetTrapFlag(0);

  /* set the tempory X and Y matrices back to empty without ref to data to
	  stop matlab "helpfully" double freeing them? */
  mxSetM(Xmx,0);mxSetN(Xmx,0);mxSetPr(Xmx,0);mxSetPi(Xmx,0);
  mxDestroyArray(Xmx);
  mxSetM(Ymx,0);mxSetN(Ymx,0);mxSetPr(Ymx,0);mxSetPi(Ymx,0);
  mxDestroyArray(Ymx);
  return Zmx;
}
