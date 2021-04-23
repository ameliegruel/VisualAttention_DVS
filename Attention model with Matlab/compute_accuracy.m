activeOutputs=length(unique(spikeTrainL2.neuronTags));
display("Number of activated Output neurons: "+int2str(activeOutputs));
display("Percentage of Output layer activation: "+num2str(round(activeOutputs/SIMU.L2_nNeurons, 3)));

% rate of neurons activating for only one category (rate coding)
rate_coding=0;                    % percentage of accuracy, aka when the neurons activated in a category do not activate in others (to minimise at 0)

% rate of neurons activating first for only one category (rank order coding)
rank_order_coding_accuracy=0;      % percentage of accuracy, aka when the neuron is first on all the samples of one category (to maximise at 1)
rank_order_coding_specificity=0;   % percentage of specificity, aka when the neuron is not first on other categories (to minimise at 0)
first_active_neurons=[];
for t=samplestime(1:end-1)
    [d, idx_closer_upper_timestamp] = min(abs(spikeTrainL2.timeStamps - t));
    first_active_neurons=[first_active_neurons spikeTrainL2.neuronTags(idx_closer_upper_timestamp)];
end

display(SIMU.nb_categories);
nb_samples_per_category=int16((length(samplestime)-1)/SIMU.nb_categories);
categories_timing=samplestime(1:nb_samples_per_category:end);
for i=1:SIMU.nb_categories 
    
    % rate coding
    index_in_category=find(spikeTrainL2.timeStamps > categories_timing(i) & spikeTrainL2.timeStamps <= categories_timing(i+1));
    if isempty(index_in_category)
        rate_coding=rate_coding+1;
    else
        active_neurons_in_category=unique(spikeTrainL2.neuronTags(index_in_category));
        for a=active_neurons_in_category
            if i==1
                active_neurons_in_other_categories=spikeTrainL2.neuronTags(index_in_category(end)+1:end);
            elseif i==SIMU.nb_categories
                active_neurons_in_other_categories=spikeTrainL2.neuronTags(1:index_in_category(1)-1);
            else
                active_neurons_in_other_categories=[spikeTrainL2.neuronTags(1:index_in_category(1)-1), spikeTrainL2.neuronTags(index_in_category(end)+1:end)];
            end
            neuron_total_nb_of_activation=length(find(active_neurons_in_other_categories==a));
            rate_coding=rate_coding + neuron_total_nb_of_activation/length(spikeTrainL2.timeStamps);
        end
    end

    % rank order coding
    %samplestime_in_category=samplestime(1+(i-1)*n:1+i*n);
    %for t=1:length(samplestime_in_category)-1
    %    index_in_sample=find(spikeTrainL2.timeStamps > samplestime_in_category(t) & spikeTrainL2.timeStamps <= samplestime_in_category(t+1));
    %    if isempty(index_in_sample)
    %        first_active_neurons = [first_active_neurons -1];
    %    else 
    %        active_neurons_in_sample=spikeTrainL2.neuronTags(index_in_sample);
    %        first_active_neuron_in_sample=active_neurons_in_sample(1);
    %        first_active_neurons = [first_active_neurons first_active_neuron_in_sample];
    %    end
    %end
    start=round(1+(i-1)*nb_samples_per_category);
    stop=round(i*nb_samples_per_category);
    display("start stop "+num2str(start)+" "+num2str(stop));
    first_active_neurons_in_category=first_active_neurons(start:stop);
    rank_order_coding_accuracy = rank_order_coding_accuracy + length(find(first_active_neurons_in_category==mode(first_active_neurons_in_category))) / nb_samples_per_category;

    for f=first_active_neurons_in_category
        if f == -1
            rank_order_coding_specificity = rank_order_coding_specificity+1;
        elseif i==1
            first_active_neuron_in_other_categories=first_active_neurons(stop+1:end);
        elseif i==SIMU.nb_categories
            first_active_neuron_in_other_categories=first_active_neurons(1:stop-1);
        else
            first_active_neuron_in_other_categories=[first_active_neurons(1:start-1) first_active_neurons(stop+1:end)];
        end
        rank_order_coding_specificity = length(find(first_active_neuron_in_other_categories==f)) / length(samplestime)-1;
    end

end

% rate coding
rate_coding = rate_coding / SIMU.nb_categories;

% rank order coding
rank_order_coding_accuracy = rank_order_coding_accuracy / SIMU.nb_categories;
rank_order_coding_specificity = rank_order_coding_specificity / SIMU.nb_categories;

display("Accuracy - rate coding: "+num2str(rate_coding));
display("Accuracy - rank order coding: "+num2str(rank_order_coding_accuracy));
display("Specificity - rank order coding: "+num2str(rank_order_coding_specificity));



%display("Accuracy - rate coding: "+num2str(latency_coding));

