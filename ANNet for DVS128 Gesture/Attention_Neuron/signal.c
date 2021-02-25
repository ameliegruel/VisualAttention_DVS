typedef struct tag_signal 
{
    double* data;
    unsigned int nData;
    unsigned short nSignals;
    int startStep;
    int stop;
    int dt;
    int line_size;
    int col_size;
} SIGNAL;

SIGNAL matlabToC_signal(const mxArray *matlabSignal) {
    SIGNAL signal;
    
    signal.data=mxGetPr(mxGetField(matlabSignal,0,"data"));
    // mxGetField : retourne un pointer vers le mxArray (1er arg - type de données nécessaire pour la routine mexFunction des fichiers C MEX, 
    //              qui demande un mxArray en input et output) dans le champs spécifié par le fieldname (3e arg) au niveau de l'index spécifié (2e arg)
    // mxGetPr : prend en entrée un pointer mxArray et retourne un pointer vers un array de données, de type mxDouble
    
    signal.nSignals=(int) mxGetScalar(mxGetField(matlabSignal,0,"nSignals"));
    signal.nData=mxGetN(mxGetField(matlabSignal,0,"data"));
    signal.startStep=(int) (mxGetScalar(mxGetField(matlabSignal,0,"start"))/mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.stop=(int) (mxGetScalar(mxGetField(matlabSignal,0,"stop"))/mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.dt = (float) (mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.line_size = (int) (mxGetScalar(mxGetField(matlabSignal,0,"line_size")));
    signal.col_size = (int) (mxGetScalar(mxGetField(matlabSignal, 0, "col_size"))); 
    return signal;
}