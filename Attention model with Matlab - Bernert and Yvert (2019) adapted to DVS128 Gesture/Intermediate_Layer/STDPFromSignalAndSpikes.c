#include "mex.h"
#include <math.h>
#include "param.c"
#include "transpo.c"
#include "signal.c"
#include "inputSpikes.c"
#include <stdlib.h>
#include <time.h>

const int nNeuronField = 15;

const	char *neuronField[15] = {
		"weight",  
   		"nextFiring",
		"firingTime",
		"nFiring",
        "lastComputedPotential",
        "lastComputationTime",
        "threshold",
        "lastPostSpike",
        "lastInhibition",
        "iWeight",
        "DNWeight",
        "resetPotential",
        "refractoryPeriod",
		"WHist",
        "PotHist"
};

typedef struct tag_neuron {
        double  **weight;
        
        int  *nextFiring;
        int  *firingTime;
        unsigned int  *nFiring;
        unsigned int     NFIRING;

        double  *lastComputedPotential;
        int  *lastComputationTime;
        
        double *threshold;

        int *lastPostSpike;
        int *lastInhibition;
        
        double *iWeight;
        double *DNWeight;
        
        double *resetPotential;
        int *refractoryPeriod;
        
		double **WHist;
        double *PotHist;
        
} NEURON,*NEURONS;

NEURON matlabToC_neuron_byIdx(mxArray *matlabNeuron, int idx) {
	NEURON neuron;
	int i;
    int j;
    int n;
	mxArray *field;

	for(i=0; i<nNeuronField; i++) {
		field = mxGetField(matlabNeuron,idx,neuronField[i]);

		if(field==NULL) { /* missing neuron field*/
			mexErrMsgIdAndTxt("missingNeuronField",neuronField[i]);
		}

		switch(i) {
			case 0:
                n=mxGetNumberOfElements(field);
                neuron.weight=mxMalloc(n*sizeof(double*));
                for (j=0;j<n;j++)
                {
                    neuron.weight[j] = mxGetPr(mxGetCell(field,j));
                }
                
				break; 
			case 1:
				neuron.nextFiring =(int*) mxGetPr(field);
				break;
			case 2:
				neuron.firingTime =(int*) mxGetPr(field);
				neuron.NFIRING = (unsigned int) mxGetN(field);
				break;
			case 3:
				neuron.nFiring =  (unsigned int*)mxGetPr(field);
				break; 
            case 4:
				neuron.lastComputedPotential =  mxGetPr(field);
				break;
            case 5:
				neuron.lastComputationTime = (int*) mxGetPr(field);
				break;
            case 6:
				neuron.threshold =  mxGetPr(field);
				break;
            case 7:
				neuron.lastPostSpike = (int*)mxGetPr(field);
				break;
            case 8:
				neuron.lastInhibition =(int*) mxGetPr(field);
				break;
            case 9:
				neuron.iWeight = mxGetPr(field);
				break;
            case 10:
				neuron.DNWeight = mxGetPr(field);
				break;
            case 11:
				neuron.resetPotential = mxGetPr(field);
				break;
            case 12:
				neuron.refractoryPeriod =(int*) mxGetPr(field);
				break;
			case 13:
                n=mxGetNumberOfElements(field);
                neuron.WHist=mxMalloc(n*sizeof(double*));
                for (j=0;j<n;j++)
                {
                    neuron.WHist[j] = mxGetPr(mxGetCell(field,j));
                }
				break;
            case 14:
				neuron.PotHist = mxGetPr(field);
				break;
		} 
	}
	return neuron;
}
NEURON matlabToC_neuron(mxArray *matlabNeuron) {
	return matlabToC_neuron_byIdx(matlabNeuron,0);
}

NEURONS matlabToC_neurons(mxArray *matlabNeuron) {
	int nNeuron = (int) mxGetN(matlabNeuron);
	NEURONS neurons = mxMalloc(nNeuron*sizeof(NEURON));
	int i;
	for(i=0; i<nNeuron; i++)
		neurons[i] = matlabToC_neuron_byIdx(matlabNeuron,i);

	return neurons;
}

double applyBoundaries(double x, double downLim,double upLim)
{
    if(x<downLim)
    {
        return downLim;
    }
    if(x>upLim)
    {
        return upLim;
    }
    return x;  
}
double maxArray(int n, double *x) {
	int i;
	double result = -mxGetInf();
	for(i=0; i<n; i++)
		if(x[i]>result)
			result = x[i];
	return result;
}
int i_round(double x) {
	return (int) (x+.5);
}


int valueInArray(int val, double arr[], int arr_length) { // retourne 1 si l'arg 1 est présent dans l'array arg 2; sinon retourne 0
    int i;
    for (i=0; i<arr_length;i++) {
        //printf("%d ",arr[i]);
        if (arr[i]==val) {
            //printf("\n");
            return 1;
        }
    }
    //printf("\n");
    return 0;
}

double * roundArray(double arr[], int size_arr) {
    double * output=malloc(size_arr*sizeof(double));
    for (int i=0; i<size_arr;i++){
        //printf("Value before rounding : %f\n", arr[i]);
        output[i] = round(arr[i]);
        //printf("Value after rounding : %f\n", output[i]);
    }
    return output;
}

// ICI TRAITEMENT DU SIGNAL EN ENTREE 
void updateAfferentSpikes(TRANSPO* transpo,SIGNAL* signal,int idx,int t)
{
    double * values;
    int x,y,z,i;
    
    for (z=transpo[idx].twindow*transpo[idx].stepSize-1;z>=transpo[idx].stepSize; z--)
    {
        for (y=transpo[idx].DVS_y-1; y>=0; y--)     // pour chaque i allant de 128*4-1 à 128
        {
            for(x=transpo[idx].DVS_x-1;x>=0;x--)    
            {
                // printf("Test 2\n");
                double temp = transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x+(z-transpo[idx].stepSize)*transpo[idx].DVS_y*transpo[idx].DVS_x];
                transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x+z*transpo[idx].DVS_y*transpo[idx].DVS_x]=temp;
                // intermediateSPikes updated : chaque spike inter est décalé de -1 indices en arrière (z), laisse de la place pour 128*128 new values à gauche
                // printf("Test 3\n");
            }
        }
    }
    // printf("Test 4\n");
    
    for (x=0;x<transpo[idx].DVS_x;x++) // pour i allant de 0 à 128 (x input)
    {
        for (y=0; y<transpo[idx].DVS_y; y++) 
        {
            // printf("Test 5\n");
            int pixel_number = y*transpo[idx].DVS_x + x ;
            values = roundArray(signal->data+( pixel_number*sizeof(double) ), signal->col_size);
            
            if (valueInArray(t,values,signal->line_size)==1)
            {
                transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x]=1;
            }
            else
            {
                transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x]=0;
                // sinon le spike correspondant au ie neurone y est mis à 0
            }
            
            free(values);
        }
    }
    
    for(z=0;z<transpo[idx].twindow;z++) // pour z allant de 0 à 4*10 (z input)
    {
        for (x=0;x<transpo[idx].DVS_x;x++)  // pour x allant de 0 à 128
        {
			for (y=0;y<transpo[idx].DVS_y;y++) 
            {
                transpo[idx].currentSpikes[x+y*transpo[idx].DVS_x+z*transpo[idx].DVS_y*transpo[idx].DVS_x] = transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x+z*transpo->stepSize*transpo[idx].DVS_y*transpo[idx].DVS_x];
                // le currentSpike correspondant au neurone de coordonnée (x=i, y=j) vaut la valeur de l'intermediate spike correspondant au neurone (x=i,y=j) de la couche d'input
            }
        }
    }
}

void updatePotential(NEURON *neuron, int time, double value ,bool absolute,PARAM *param)
{
    int dt=time-(*neuron->lastComputationTime);
    
    /*update*/
    
    if(!absolute&&dt<param->tm*20)
    {
        (*neuron->lastComputedPotential)=(*neuron->lastComputedPotential)*param->expTm[dt]+value;
    }
    else
    {
        (*neuron->lastComputedPotential)=value;
    }
    (*neuron->lastComputationTime)=time;
    
    /*update next firing time*/
    if(mxIsInf(*neuron->threshold)||*(neuron->lastComputedPotential)<*neuron->threshold)
    {
        *(neuron->nextFiring)=-1;//no firing scheduled, no additional computation needed
    }
    else
    {
        if(*neuron->lastPostSpike>=0&&*neuron->lastPostSpike+ *neuron->refractoryPeriod>time)
        {
            int t=*neuron->lastPostSpike+ *neuron->refractoryPeriod;//end of refractory period
            double pot=0;
            if((t-time)<param->tm*20)
            {
                pot=(*(neuron->lastComputedPotential)*param->expTm[t-time]);//potential at the end of refractory period
            }
            if(pot>=*neuron->threshold)
            {
                *(neuron->nextFiring)=t;//next spike at the end of refractory period
            }
            else
            {
                *(neuron->nextFiring) = -1;
            }
        }
        else
        {
            *(neuron->nextFiring)=time; 
        }
    }
}

void integrate(NEURON *neuron, int time,unsigned short sig ,unsigned short afferent, PARAM *param,TRANSPO *transpo) {

    double w;

    w=neuron->weight[sig][afferent];

    /*STDP*/
    if(!param->freezeSTDP)
    {
        
        if(*(neuron->lastPostSpike)>=0&&(time-*(neuron->lastPostSpike))<=param->stdp_t_neg)
        {
            neuron->weight[sig][afferent]+=param->stdp_a_neg;
            neuron->weight[sig][afferent]=applyBoundaries(neuron->weight[sig][afferent],0,1);
        }
        
    }
    

    /*update potential and next firing time*/
    updatePotential(neuron,time,w,false,param);
    
}


void fire(NEURON *neuron, int time, PARAM *param,TRANSPO *transpo,int nSig) {
    
    /*STDP*/
    
    int aff=0;
    int sig=0;
    
    *(neuron->lastPostSpike)=time;
    if(!param->freezeSTDP)
    {
        for (sig=0;sig<nSig;sig++)
        {
            for(aff=0;aff<transpo[sig].nAfferents;aff++)
            {
                
                    neuron->weight[sig][aff]+=param->cte_ltd;
                    if(transpo[sig].lastPreSpike[aff]>=0&&(time-transpo[sig].lastPreSpike[aff])<=param->stdp_t_pos)
                    {
                        neuron->weight[sig][aff]+=param->stdp_a_pos;
                    }
                    neuron->weight[sig][aff]=applyBoundaries(neuron->weight[sig][aff],0,1);
                
            }
        }
    }

    
	/* postsynaptique spike count */
	*(neuron->nFiring) += 1;

	/* postsynaptique spike times */
	(*neuron).firingTime[((int)*(*neuron).nFiring-1)%(*neuron).NFIRING] = time;

	/* update Potential */
    updatePotential(neuron,time,*(neuron->resetPotential),true,param);
   
}

void applyInhibition(NEURON *postNeuron,int preNeuronIdx, int time, PARAM *param,TRANSPO *transpo,int nSig)
{
    updatePotential(postNeuron,time,-postNeuron->iWeight[preNeuronIdx],true,param);
}


// 0-neuron, 1-struct(signal), 2-INPUTSPIKES, 3-SPIKETRANSPOSITION, 4-PARAM_L1, 5-start, 6-stop
void
mexFunction(	int nlhs, mxArray *plhs[],
				int nrhs, const mxArray *prhs[] )
{
	if(nrhs==7) 
    {
        /* variables */
        mxArray *output = mxDuplicateArray(prhs[0]); /* neurons */
        mxArray *outputTranspo = mxDuplicateArray(prhs[3]);
        NEURONS neuron = matlabToC_neurons(output);	/* get neurons from matlab structure */
        SIGNAL signal = matlabToC_signal(prhs[1]);/*signal*/
        INPUTSPIKES inputSpikes=matlabToC_inputSpikes(prhs[2]);
        TRANSPO* transpo=matlabToC_transpos(outputTranspo); /* transposition */
        PARAM param = matlabToC_param(prhs[4]); /* param */
        
        int t, nextFiring = -1;
        int s=0;
        unsigned short i, nNeuron = mxGetN(prhs[0]), nextOneToFire;
        unsigned short nTranspos=mxGetN(prhs[3]);
        int start = (int)mxGetScalar(prhs[5]);
        int stop = (int)mxGetScalar(prhs[6]);
        
		int wIdx=0;
		int nextWtime=0;
        int nStepsW=ceil(param.WHistDuration/param.WHistStep);
        int potIdx=0;
        int nextPottime=0;
        
         /* affects output */
        plhs[0] = output;
        plhs[1] = outputTranspo;
        
        /*init next firing*/
        nextFiring=-1;
        for(i=0; i<nNeuron; i++)
        {
            if(*(neuron[i].nextFiring)!=-1)
            {
                updatePotential(&neuron[i],start,0,false,&param);
                if((nextFiring==-1||*(neuron[i].nextFiring)<nextFiring)&&*(neuron[i].nextFiring)>=start)
                {
                    nextOneToFire = i;
                    nextFiring = *(neuron[i].nextFiring);
                }
                else if(*(neuron[i].nextFiring)==nextFiring
                        &&*neuron[i].lastComputedPotential>*neuron[nextOneToFire].lastComputedPotential)
                {
                    nextOneToFire = i;
                    nextFiring = *(neuron[i].nextFiring);
                }
            }
        }
        
        //check time range
        // if(start<signal.startStep||stop>signal.startStep+signal.nData)
        // {
        //     mexErrMsgIdAndTxt("timeRangeError","outside data time range,%d-%d,%d-%d\n",start,stop,signal.startStep,signal.startStep+signal.nData);
        // }
        
        // main loop (time)
        for (t=start;t<stop;t++)
        {
            int aff=0;
            int sig=0;
            
            // printf("test 1\n");
            //presynaptic spikes from spiketrain
            while(s<inputSpikes.nSpikes&&inputSpikes.timeStamps[s]<t)
            {
                for(i=0; i<nNeuron; i++)
                {
                    updatePotential(&neuron[i],t,*(neuron[0].DNWeight),false,&param);
                }
                s++;
            }
            
           //presynaptic spikes loop (integrate)
            updateAfferentSpikes(transpo,&signal, sig,t);
                
            for(aff=0;aff<transpo[sig].nAfferents;aff++)
            {/*presynaptic spikes*/
                int dt;
                if(transpo[sig].currentSpikes[aff]==1)
                {
                    
                    transpo[sig].lastPreSpike[aff]=t;
                    
                    /* integrate this spike */
                    for(i=0; i<nNeuron; i++)
                    {
                        
                        integrate(&neuron[i],t,sig,aff,&param,transpo);
                        
                    }
                }
            }
            
            //postsynaptic spikes loop
            nextFiring = -1;
            for(i=0; i<nNeuron; i++)
            {
                if(*(neuron[i].nextFiring)!=-1)
                {
                    updatePotential(&neuron[i],t,0,false,&param);
                    if((nextFiring==-1||*(neuron[i].nextFiring)<nextFiring)&&*(neuron[i].nextFiring)>=start)
                    {
                        nextOneToFire = i;
                        nextFiring = *(neuron[i].nextFiring);
                    }
                    else if(*(neuron[i].nextFiring)==nextFiring
                            &&*neuron[i].lastComputedPotential>*neuron[nextOneToFire].lastComputedPotential)
                    {
                        nextOneToFire = i;
                        nextFiring = *(neuron[i].nextFiring);
                    }
                }
            }
            
            while(nextFiring!=-1&&nextFiring <= t)
            { /* next event is a postsynaptic spike */
                
                /* the winner fires */
                fire(&neuron[nextOneToFire],t,&param,transpo,signal.nSignals);
                
                /*inhibition*/
                for(i=0;i<nNeuron;i++)
                {
                    applyInhibition(&neuron[i],nextOneToFire,t,&param,transpo,signal.nSignals);
                }
                
                /* remove scheduled firing */
                nextFiring = -1;
                for(i=0; i<nNeuron; i++)
                {
                    if(*(neuron[i].nextFiring)!=-1)
                    {
                        updatePotential(&neuron[i],t,0,false,&param);
                        if((nextFiring==-1||*(neuron[i].nextFiring)<nextFiring)&&*(neuron[i].nextFiring)>=start)
                        {
                            nextOneToFire = i;
                            nextFiring = *(neuron[i].nextFiring);
                        }
                        else if(*(neuron[i].nextFiring)==nextFiring
                                &&*neuron[i].lastComputedPotential>*neuron[nextOneToFire].lastComputedPotential)
                        {
                            nextOneToFire = i;
                            nextFiring = *(neuron[i].nextFiring);
                        }
                    }
                }
            }
            
            
            //History update
            //WHist
            if (t+1>=nextWtime&&nextWtime<=param.WHistDuration)
            {
                int sig,n=0;
                int aff=0;
                for(n=0; n<nNeuron; n++)
                {
                    for(sig=0;sig<signal.nSignals;sig++)
                    {
                        for(aff=0;aff<transpo[sig].nAfferents;aff++)
                        {
                            neuron[n].WHist[sig*nStepsW+wIdx][aff]=neuron[n].weight[sig][aff];
                        }
                    }
                }
                wIdx++;
                nextWtime=nextWtime+param.WHistStep;
            }
            
            
            //PotHist
            if (t>=nextPottime&&t<param.PotHistDuration)
            {
                int i=0;
                for(i=0; i<nNeuron; i++)
                {
                    updatePotential(&neuron[i],t,0,false,&param);
                    neuron[i].PotHist[potIdx]=*neuron[i].lastComputedPotential;
                }
                potIdx++;
                nextPottime=nextPottime+param.PotHistStep;
            }

            printf("Simulation done for t=%d\n", t);
        }
        
        for(i=0; i<nNeuron; i++)
        {
            mxFree(neuron[i].weight);
            mxFree(neuron[i].WHist);
        }
        mxFree(neuron);
        mexPrintf("done\n");
    }
    
}
