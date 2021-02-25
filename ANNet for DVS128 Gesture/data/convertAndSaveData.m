function [signal] = convertAndSaveData(samples,timeStep,filename)
%CONVERTANDSAVEDATA Summary of this function goes here
%   Detailed explanation goes here
    signal.nSignals=size(samples,1);
    signal.start=0;
    signal.dt=1/80000;
    if(timeStep==1/80000)
        signal.data=samples;
    else
        times=0:signal.dt:((size(samples,2)-1)*timeStep);
        samples=[samples,samples(:,end)];
        
        idx=floor(times/timeStep);
        l=times/timeStep-idx;
        signal.data=zeros(signal.nSignals,length(times));
        for i=1:signal.nSignals
            signal.data(i,:)=samples(i,idx+1).*(1-l)+samples(i,idx+2).*l;
        end
    end
    
    save(filename,'signal');
end

