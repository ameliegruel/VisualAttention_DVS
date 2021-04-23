SIMU.categories=[];

for i=1:SIMU.nb_categories
    SIMU.categories=[SIMU.categories ; eval(['SIMU.cat' num2str(i)]) samplestime(int16(length(samplestime)/SIMU.nb_categories*i))];
end

% Scatter plot of neurons activation accross time in the 3 layers

figure();
suptitle({"Simulation results for DVS128 Gesture over "+int2str(stop)+" ms"});

subplot(3,1,1);
plotSpikeTrain(spikeTrainAN,start,stop);
ylabel("Attention neuron");
for cat=SIMU.categories(:,2)
    line([cat cat], [0.5 SIMU.DN_nNeurons+0.5]);
end
hold off;

subplot(3,1,2);
plotSpikeTrain(spikeTrainL1,start,stop);
ylabel("Intermediate layer");
for cat=SIMU.categories(:,2)
    line([cat cat], [0 SIMU.L1_nNeurons]);
end
hold off;

subplot(3,1,3);
plotSpikeTrain(spikeTrainL2,start,stop),
ylabel("Output layer");
xlabel("Time (in ms)");
for cat=SIMU.categories(:,2)
    line([cat cat], [0 SIMU.L2_nNeurons]);
end

% Evolution of the weight in the 3 layers

