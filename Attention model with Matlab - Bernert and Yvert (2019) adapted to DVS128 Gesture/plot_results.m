figure;
suptitle({"Simulation results for DVS128 Gesture over "+int2str(stop)+" ms","Hand gesture category : right hand counter clockwise (5)"});
subplot(3,1,1);
plotSpikeTrain(spikeTrainAN,start,stop);
ylabel("Attention neuron");
hold off;
subplot(3,1,2);
plotSpikeTrain(spikeTrainL1,start,stop);
ylabel("Intermediate layer");
hold off;
subplot(3,1,3);
plotSpikeTrain(spikeTrainL2,start,stop),
ylabel("Output layer");
xlabel("Time (in ms)");

% plotPotHist(L1PotHist,step)
% plotPotHist(L1ThHist,step)