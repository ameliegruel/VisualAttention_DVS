%file names
inputFile='gesture_data.mat';
inputFolder='../data/';

AN_simu_name='ANtest';
AN_saveFolder='';

%load files
load([inputFolder inputFile]);
format long g;
signal.data = gesturedata; 
signal.nSignals=1;
signal.dt=1.25e-5;
signal.start=0;
signal.line_size=size(signal.data,2); % number of pixels in DVS camere (DVS_x*DVS_y)
signal.col_size=size(signal.data,1);  % maximum number of events that happened at least once on one pixel
signal.stop= round(max(max(signal.data)));

%prepare parameters
simuparameter;
PARAM_DN=createParamDN(SIMU);
SPIKETRANSPOSITION=prepareSpikeTransposition(SIMU,signal);
neuron = createNewDNNeuron(SIMU,size(signal.data,2));

%run simulation
%start=signal.start/signal.dt;
%stop=start+signal.stop/signal.dt;
start=signal.start;
stop = start+signal.stop;
tic
[neuron]=DNFromSignal(neuron,struct(signal),SPIKETRANSPOSITION,PARAM_DN,start,stop);
toc
  
%save results
%spikeTrainD=convertNeuronToSpikeTrain(neuron,1/signal.dt,start,stop);
spikeTrainAN=convertNeuronToSpikeTrain(neuron,signal.dt);
ANPotHist=neuron.PotHist;

resultfile=[AN_saveFolder AN_simu_name '_on_' inputFile];
save(resultfile,'spikeTrainAN','SIMU','ANPotHist');
        


