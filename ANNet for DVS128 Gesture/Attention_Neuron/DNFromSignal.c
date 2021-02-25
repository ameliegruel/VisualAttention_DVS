#include "mex.h"
#include <math.h>
#include "param.c"
#include "transpo.c"
#include "signal.c"
#include <stdlib.h>
#include <time.h>

const int nNeuronField = 8;

const	char *neuronField[8] = { 
   		"nextFiring",
		"firingTime",
		"nFiring",
        "lastComputedPotential",
        "lastComputationTime",
        "threshold",
        "resetPotential",
        "PotHist"
};

typedef struct tag_neuron {
        
        int  *nextFiring;
        int  *firingTime;
        unsigned int  *nFiring;
        unsigned int     NFIRING;

        double  *lastComputedPotential;
        int  *lastComputationTime;
        
        double *threshold;
        
        double *resetPotential;

        double *PotHist;
        
} NEURON,*NEURONS;

NEURON matlabToC_neuron_byIdx(mxArray *matlabNeuron, int idx) {    // for each neuron given into input by its idx, update the 8 neuronField according to Matlab's neuron information
    NEURON neuron;
	int i;
	mxArray *field;

	for(i=0; i<nNeuronField; i++) {
		field = mxGetField(matlabNeuron,idx,neuronField[i]);
        // mxGetField : retourne un pointer vers le mxArray (1er arg - type de données nécessaire pour la routine mexFunction des fichiers C MEX, qui demande un mxArray en input et output) dans le champs spécifié par le fieldname (3e arg) au niveau de l'index spécifié (2e arg)
	
		if(field==NULL) { /* missing neuron field*/
			mexErrMsgIdAndTxt("missingNeuronField",neuronField[i]);
		}

		switch(i) {
			case 0:
				neuron.nextFiring =(int*) mxGetPr(field);
				break;
			case 1:
				neuron.firingTime =(int*) mxGetPr(field);
				neuron.NFIRING = (unsigned int) mxGetN(field);
				break;
			case 2:
				neuron.nFiring =  (unsigned int*)mxGetPr(field);
				break; 
            case 3:
				neuron.lastComputedPotential =  mxGetPr(field);
				break;
            case 4:
				neuron.lastComputationTime = (int*) mxGetPr(field);
				break;
            case 5:
				neuron.threshold =  mxGetPr(field);
				break;
            case 6:
				neuron.resetPotential = mxGetPr(field);
				break;
            case 7:
				neuron.PotHist = mxGetPr(field);
				break;
		} 
	}
	return neuron;
}
NEURON matlabToC_neuron(mxArray *matlabNeuron) {     // converts first Matlab neuron in C neuron using function matlabToC_neuron_byIdx
	return matlabToC_neuron_byIdx(matlabNeuron,0);
}

NEURONS matlabToC_neurons(mxArray *matlabNeuron) {  // convert 
	int nNeuron = (int) mxGetN(matlabNeuron);  // get number of neurons
	NEURONS neurons = mxMalloc(nNeuron*sizeof(NEURON));  // mxMalloc() : allocate uninitialized dynamic memory using MATLAB memory manager
	int i;
	for(i=0; i<nNeuron; i++)
		neurons[i] = matlabToC_neuron_byIdx(matlabNeuron,i);  // for each neuron defined in Matlab, create C neuron

	return neurons;
}

double applyBoundaries(double x, double downLim,double upLim)  // set boundaries between downLim and upLim
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
double maxArray(int n, double *x) {   // retourne la valeur maximale de l'array donné en input
	int i;
	double result = -mxGetInf();  // mxGetInf returns the value of Matlab internal infinity variable
	for(i=0; i<n; i++)
		if(x[i]>result)
			result = x[i];
	return result;
}
int i_round(double x) {   // retourne la valeur arrondie supérieure de la variable donnée en input
	return (int) (x+.5);
}

int valueInArray(int val, double arr[], int arr_length) { // retourne 1 si l'arg 1 est présent dans l'array arg 2; sinon retourne 0
    int i;
    for (i=0; i<arr_length;i++) {
        printf("%d ",arr[i]);
        if (arr[i]==val) {
            printf("\n");
            return 1;
        }
    }
    printf("\n");
    return 0;
}

double * roundArray(double arr[], int size_arr) {
    double * output=malloc(size_arr*sizeof(double));
    for (int i=0; i<size_arr;i++){
        printf("Value before rounding : %f\n", arr[i]);
        output[i] = round(arr[i]);
        printf("Value after rounding : %f\n", output[i]);
    }
    return output;
}

// ICI TRAITEMENT DU SIGNAL EN ENTREE 
void updateAfferentSpikes(TRANSPO* transpo,SIGNAL* signal,int idx,int t)  // appelé en début de simulation pour chaque signal donné en entrée
{
    double * values;
    
    //values = malloc(signal->stop*sizeof(double));
    int x,y,z,i;
    
    // value=signal->data[signal->nSignals*(t-signal->startStep)+idx];  
    // value contient la valeur de signal du temps correspondant (t actuel - début du signal)
    // idx vaut 1 (nombre de signaux)
    
    for(x=transpo[idx].DVS_x-1;x>=0;x--)    // pour chaque i allant de 128*4-1 à 128
    {
        for (y=transpo[idx].DVS_y-1; y>=0; y--) 
        {
            for (z=transpo[idx].twindow*transpo[idx].stepSize-1;z>=transpo[idx].twindow; z--){
                printf("Boucle à la con : x = %d, y = %d, z=%d ", x, y, z);
                double temp = transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x+(z-1)*transpo[idx].DVS_y*transpo[idx].DVS_x];
                printf("temp: %f\n", temp);
                transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x+z*transpo[idx].DVS_y*transpo[idx].DVS_x]=temp;
                // intermediateSPikes updated : chaque spike inter est décalé de -1 indices en arrière (z), laisse de la place pour 128*128 new values à gauche
            }
        }
    }
    printf("fin boucle à la con\n");
    
    
    for (x=0;x<transpo[idx].DVS_x;x++) // pour i allant de 0 à 128 (x input)
    {
        for (y=0; y<transpo[idx].DVS_y; y++) 
        {
            values = roundArray(signal->data+((y-1)*transpo[idx].DVS_y + x)*sizeof(double), signal->col_size);
            printf("Roundarray called for x=%d and y=%d\n", x, y);
            
            if (valueInArray(t,values,signal->line_size)==1)
            // if(valueInArray(round(t*signal->dt),values)==1)  
            // si le temps t est présent dans gesturedata[x,y], le pixel correspondant a reçu un spike au temps correspondant
            {
                transpo[idx].intermediateSpikes[x+y*transpo[idx].DVS_x]=1;
                // le spike correspondant au ie neurone y (en début de interSpikes donc t le plus récent) est mis à 1
                printf("Time : %d\n",t);
                printf("Pixel x=%d et y=%d\n",x,y);
                printf("Values : ");
                for (i=0; i<signal->line_size;i++) {
                    printf("%f ", values[i]);
                }
                printf("\n\n");
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
       *(neuron->nextFiring)=time; 
    }
}

void integrate(NEURON *neuron, int time,unsigned short sig ,unsigned short afferent, PARAM *param,TRANSPO *transpo) {

    double w;
    w=transpo[sig].pRel[afferent];

    /*update potential and next firing time*/
    updatePotential(neuron,time,w,false,param);
    
}


void fire(NEURON *neuron, int time, PARAM *param,TRANSPO *transpo,int nSig) {

	/* postsynaptique spike count */
	*(neuron->nFiring) += 1;

	/* postsynaptique spike times */
	(*neuron).firingTime[((int)*(*neuron).nFiring-1)%(*neuron).NFIRING] = time;

	/* update Potential */
    updatePotential(neuron,time,*(neuron->resetPotential),false,param);
   
}



// DNFromSignal(0-neuron, 1-struct(signal), 2-SPIKETRANSPOSITION, 3-PARAM_DN, 4-start, 5-stop)
// struct() : crée une structure scalare avec des noms de champs et des valeurs correspondant aux propriétés de l'objet 
void
mexFunction(	int nlhs, mxArray *plhs[],     // nlhs : nombre d'arguments en output 
                                               // plhs : array de pointers vers les arguments en output attendus, du type mxArray 
				int nrhs, const mxArray *prhs[] )  // nrhs : nombre d'arguments en input
                                                   // prhs : array de pointers vers les arguments mxArray input
{
    if(nrhs==6) 
    {
        /* variables */
        mxArray *output = mxDuplicateArray(prhs[0]); /* neurons */
        mxArray *outputTranspo = mxDuplicateArray(prhs[2]);  // mxDuplicateArray(): make deep copy of array => creates a duplicata of SPIKETRANSPO
        NEURONS neuron = matlabToC_neurons(output);	/* get neurons from matlab structure */
        SIGNAL signal = matlabToC_signal(prhs[1]); /* signal */
        // crée un objet signal compréhensible en C à partir de l'objet signal Matlab
        
        printf("blablabla %f\n",signal.data[12+2*16384]);
        
        TRANSPO* transpo=matlabToC_transpos(outputTranspo); /* transposition : modifies the duplicata of Matlab SPIKETRANSPO into C object, with no modification of content */
        PARAM param = matlabToC_param(prhs[3]); /* param : parameters of Attention neuron from Matlab to C */
        
        int t;
        unsigned short i;
        unsigned short nTranspos=mxGetN(prhs[2]);
        int start = (int)mxGetScalar(prhs[4]);
        //int stop = (int)mxGetScalar(prhs[5]);
        int stop = 2;
        printf("%d\n", stop);

        int potIdx=0;
        int nextPottime=0;
        
         /* affects output */
        plhs[0] = output;
        plhs[1] = outputTranspo;
        
        //check time range
        /*
        if(start<signal.startStep||stop>signal.startStep+signal.nData)
        {
            mexErrMsgIdAndTxt("timeRangeError","outside data time range,%d-%d,%d-%d\n",start,stop,signal.startStep,signal.startStep+signal.nData);
        }
         */
        printf("// Start simulation //\n");
        
        // main loop (time)
        // SIMULATION START
        for (t=start;t<stop;t++)   
        {
            int aff=0;
            int sig=0;
            printf("bla\n");
            updateAfferentSpikes(transpo,&signal, sig,t); 
            // update les valeurs de spikes entrant selon la valeur donnée en entrée par le signal
            // avec sig le nombre de signal (1) et t le temps
            printf("blo\n");
            
            for(aff=0;aff<transpo[sig].nAfferents;aff++)  // pour chaque neurone de la couche d'entrée
                {/*presynaptic spikes*/
                int dt;
                if(transpo[sig].currentSpikes[aff]==1)  // si ce neurone est actif à l'instant t => calcul de la STP => POURQUOI ??
                {
                    printf("YESSSSSSSSSSSSSSSSSSSSSSSSSSSSss\n");
                    /*Prel update 1st step*/
                    dt=t - transpo[sig].pRelLastComputation[aff];  
                    if(dt<param.std_t*20)
                    {
                        transpo[sig].pRel[aff]=1-(1-transpo[sig].pRel[aff])*param.expTd[dt];
                    }
                    else
                    {
                        transpo[sig].pRel[aff]=1;
                    }

                    transpo[sig].lastPreSpike[aff]=t;

                    /* integrate this spike */
                    integrate(&neuron[0],t,sig,aff,&param,transpo);


                    /*Prel update 2nd step*/
                    transpo[sig].pRel[aff]=transpo[sig].pRel[aff]*(1-param.std_fd);
                    transpo[sig].pRelLastComputation[aff]=t;
                }
            }

            //postsynaptic spikes loop
            if(*neuron[0].nextFiring == t)
            { /* next event is a postsynaptic spike */
                
                /* the winner fires */
                fire(&neuron[0],t,&param,transpo,signal.nSignals);
                
            }
            
            
            //PotHist
            if (t>=nextPottime&&t<param.PotHistDuration)
            {
                
                updatePotential(&neuron[0],t,0,false,&param);
                neuron[0].PotHist[potIdx]=*neuron[0].lastComputedPotential;

                potIdx++;
                nextPottime=nextPottime+param.PotHistStep;
            }
        }
        
        
        mxFree(neuron);
        mexPrintf("done\n");
    }
    
}
