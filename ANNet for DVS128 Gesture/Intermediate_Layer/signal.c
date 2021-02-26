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
    signal.nSignals=(int) mxGetScalar(mxGetField(matlabSignal,0,"nSignals"));
    signal.nData=mxGetN(mxGetField(matlabSignal,0,"data"));
    signal.startStep=(int) (mxGetScalar(mxGetField(matlabSignal,0,"start"))/mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.stop=(int) (mxGetScalar(mxGetField(matlabSignal,0,"stop"))/mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.dt = (float) (mxGetScalar(mxGetField(matlabSignal,0,"dt")));
    signal.line_size = (int) (mxGetScalar(mxGetField(matlabSignal,0,"line_size")));
    signal.col_size = (int) (mxGetScalar(mxGetField(matlabSignal, 0, "col_size")));
    return signal;
}