function [] = plotSpikeTrain(spikes,start,stop)
%PLOTSPIKETRAIN Summary of this function goes here
%   Detailed explanation goes here
C=myColors(spikes.nNeurons);
for n=1:spikes.nNeurons
    idx=((spikes.neuronTags==n)&spikes.timeStamps>=start&spikes.timeStamps<stop);
    t=spikes.timeStamps(idx);
    %display(t);
    %x=[t;t];
    %display(x);
    % plot([t;t],[zeros(size(t));ones(size(t))],'Color',C(n,:)); hold on;  % hold on retains current plot when adding new plots
    scatter(t, ones(size(t))*n); hold on;
end
end

