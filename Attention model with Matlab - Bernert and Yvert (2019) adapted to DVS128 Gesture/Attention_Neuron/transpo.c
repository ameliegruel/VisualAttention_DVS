const int nTranspoField = 10;
const	char *transpoField[10] = {
               
          "DVS_x",
          "DVS_y",
          "DVm",
          "twindow",
          "stepSize",
          "currentSpikes",
          "intermediateSpikes",
          "Prel",
          "PrelLastComputation",
          "lastPreSpike"
          
};

typedef struct tag_transpo {

unsigned short DVS_x;
unsigned short DVS_y;
// unsigned short nCenters;
double DVm;
unsigned short twindow;
unsigned short stepSize;
bool* currentSpikes;
bool* intermediateSpikes;
unsigned short nAfferents;
double *pRel;
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
			mexErrMsgIdAndTxt("missingParamField",transpoField[i]);
		}

		switch(i) {
			case 0:
				transpo.DVS_x = mxGetScalar(field);  
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
				transpo.currentSpikes =(bool*) mxGetPr(field);
				break;
            case 6:
				transpo.intermediateSpikes =(bool*) mxGetPr(field);
				break;
            case 7:
				transpo.pRel = mxGetPr(field);
				break;
            case 8:
				transpo.pRelLastComputation =(int*) mxGetPr(field);
				break;
            case 9:
				transpo.lastPreSpike = (int*)mxGetPr(field);
				break;
		} 
	}
    transpo.nAfferents = transpo.DVS_x*transpo.DVS_y*transpo.twindow;
	return transpo;
}

TRANSPO* matlabToC_transpos(mxArray *matlabTranspo) {  // for 
	int nTranspo = (int) mxGetN(matlabTranspo);  // get number of columns in Matlab SPIKETRANSPO
	TRANSPO* transpos = mxMalloc(nTranspo*sizeof(TRANSPO));
	int i;
	for(i=0; i<nTranspo; i++)   // pour toutes les colonnes de SPIKETRANSPO (1 seule ?) transforme celle ci en objet transpo C
		transpos[i] = matlabToC_transpo_byIdx(matlabTranspo,i);

	return transpos;
}
