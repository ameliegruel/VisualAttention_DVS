const int nTranspoField = 11;
const	char *transpoField[11] = {
               
          "DVS_x",
		  "DVS_y",
          "DVm",
          "twindow",
          "stepSize",
          "currentSpikes",
          "intermediateSpikes",
          "Prel",
          "Fd",
          "PrelLastComputation",
          "lastPreSpike"
          
};

typedef struct tag_transpo {

unsigned short DVS_x;
unsigned short DVS_y;
double DVm;
unsigned short twindow;
unsigned short stepSize;
bool* currentSpikes;
bool* intermediateSpikes;
unsigned short nAfferents;
double *pRel;
double *Fd;
int *pRelLastComputation;
int *lastPreSpike;

} TRANSPO;

TRANSPO matlabToC_transpo_byIdx(const mxArray *matlabTranspo,int idx) {
	TRANSPO transpo;
	int i;
	mxArray *field;

	for(i=0; i<nTranspoField; i++) {
		field = mxGetField(matlabTranspo,idx,transpoField[i]);

		if(field==NULL) { /* missing param field */
			mexPrintf("Missing parameter field:");
			mexErrMsgIdAndTxt("missingParameterField",transpoField[i]);
		}

		switch(i) {
			case 0:
				transpo.DVS_x  = mxGetScalar(field);
            	break;
			case 1:
				transpo.DVS_y = mxGetScalar(field);
				break;
			case 2:
				transpo.DVm = mxGetScalar(field);
				break;
            case 3:
				transpo.twindow = mxGetScalar(field);
				break;
            case 4:
				transpo.stepSize = mxGetScalar(field);
				break;
            case 5:
				transpo.currentSpikes = (bool*)mxGetPr(field);
				break;
            case 6:
				transpo.intermediateSpikes =(bool*) mxGetPr(field);
				break;
            case 7:
				transpo.pRel = mxGetPr(field);
				break;
            case 8:
				transpo.Fd = mxGetPr(field);
				break;
            case 9:
				transpo.pRelLastComputation = (int*)mxGetPr(field);
				break;
            case 10:
				transpo.lastPreSpike =(int*) mxGetPr(field);
				break;
		} 
	}
	transpo.nAfferents = transpo.DVS_x*transpo.DVS_y*transpo.twindow;
	return transpo;
}

TRANSPO* matlabToC_transpos(mxArray *matlabTranspo) {
	int nTranspo = (int) mxGetN(matlabTranspo);
	TRANSPO* transpos = mxMalloc(nTranspo*sizeof(TRANSPO));
	int i;
	for(i=0; i<nTranspo; i++)
		transpos[i] = matlabToC_transpo_byIdx(matlabTranspo,i);

	return transpos;
}
