function [ SPIKETRANSPOSITION ] = prepareSpikeTransposition( SIMU,signal )
%PREPARESPIKETRANSPOSITION Summary of this function goes here
%   Detailed explanation goes here

%s_noise=median(signal.data)/0.6745;

SPIKETRANSPOSITION=[];

for i=1:signal.nSignals
    SPIKETRANSPOSITION(i).overlap=SIMU.TR_overlap;
    SPIKETRANSPOSITION(i).DVm=SIMU.TR_DVmF;%*s_noise
    
    SPIKETRANSPOSITION(i).twindow=uint16(SIMU.TR_winSize); % window of delays (x of input)
    SPIKETRANSPOSITION(i).stepSize=uint16(SIMU.TR_stepSize); % stepsize ? 
    
    %minVal=min(signal.data);
    %maxVal=max(signal.data);
    
    DVm=SPIKETRANSPOSITION(i).DVm;
    DVi=DVm*2/SIMU.TR_overlap;
    
    
    %SPIKETRANSPOSITION(i).centers=(minVal-DVm):DVi:(maxVal+DVm);  % intervalle de minVal-DVm (-11.2) à maxVal+DVm (16.2)
    SPIKETRANSPOSITION(i).DVS_x=128;
    SPIKETRANSPOSITION(i).DVS_y=128;
    SPIKETRANSPOSITION(i).nAff=SPIKETRANSPOSITION(i).twindow*SPIKETRANSPOSITION(i).DVS_x*SPIKETRANSPOSITION(i).DVS_y;  % nombre de neurones dans input
    SPIKETRANSPOSITION(i).currentSpikes=logical(zeros(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y, SPIKETRANSPOSITION(i).twindow));  % 3D array of zeros, of size (x=128,y=128,z=10) and converted to array of logical values with logical()
    SPIKETRANSPOSITION(i).intermediateSpikes=logical(zeros(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y,SIMU.TR_stepSize*SPIKETRANSPOSITION(i).twindow));  % 3D array of zeros of size (x=128,y=128,z=4*10), and converted to array of logical values
    
    SPIKETRANSPOSITION(i).Prel=zeros(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y, SPIKETRANSPOSITION(i).twindow); % Prel ?? - 2D array of zeros of size (y=84,x=10)
    SPIKETRANSPOSITION(i).Fd=zeros(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y, SPIKETRANSPOSITION(i).twindow);  % short term plasticity depression factor -- 2D array of zeros, of size (y=84,x=10)
    SPIKETRANSPOSITION(i).PrelLastComputation=int32(zeros(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y, SPIKETRANSPOSITION(i).twindow)); %  
    SPIKETRANSPOSITION(i).lastPreSpike=int32(-1*ones(SPIKETRANSPOSITION(i).DVS_x, SPIKETRANSPOSITION(i).DVS_y, SPIKETRANSPOSITION(i).twindow));      % 2D array of -1 of size (y=84,x=10)
    % NB : int32() : transforms into 32-bit signed integer arrays
    
end
end

