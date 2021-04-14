#!/bin/bash

now=`date +"%F_%H-%M-%S"`
mkdir Results/Simu_$now/
touch Results/Simu_$now/Simulation_$now.csv
echo "Simulation loop;Category;Number of events;Bigger timestamp;" >> Results/Simu_$now/Simulation_$now.csv

# parameters Attention
thresholdAttention=25
tmAttention=2

# parameters Inter
thresholdInter=25
tmInter=0.025
nbInterNeurons=60

# parameters Output
thresholdOutput=25
tmOutput=240
nbOutputNeurons=11

# save parameters
touch Results/Simu_$now/Parameters_Simu_$now.csv
echo "Simulation loop;Number of active output neurons;Activation rate of output layer;Specific activation rate;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" > Results/Simu_$now/Parameters_Simu_$now.csv

# define matlab commands 
import_data="gesturedata=importdata('data/gesture_data.csv');samplestime=importdata('data/samples_time.csv');save('data/gesture_data.mat','gesturedata','-v7.3');"
Attention_parameters="SIMU.DN_tm=$tmAttention;SIMU.DN_threshold=$thresholdAttention;"
Intermediate_parameters="SIMU.L1_tm=$tmInter;SIMU.L1_threshold=$thresholdInter;SIMU.L1_nNeurons=$nbInterNeurons;"
Output_parameters="SIMU.L2_tm=$tmOutput;SIMU.L2_maxTh=$thresholdOutput;SIMU.L2_nNeurons=$nbOutputNeurons;"
run_scripts="run('Attention_Neuron/runScriptDN.m');run('Intermediate_Layer/runScriptL1.m');run('Output_Layer/runScriptL2.m');"
run_accuracy="run('compute_accuracy.m');"
exit="exit;"


s=1
nbSimu=10

# main loop
while ((s <= nbSimu))
do 
    echo "// SIMULATION LOOP $s //"

    # get categories
    cat_max=11
    cat1=$RANDOM
    let "cat1 %= $cat_max" 
    
    cat2=$RANDOM
    let "cat2 %= $cat_max"
    while [ $cat2 -eq $cat1 ]
    do 
        cat2=$RANDOM
        let "cat2 %= $cat_max"
    done

    cat3=$RANDOM 
    let "cat3 %= $cat_max"
    while (( cat3 == cat2 || cat3 == cat1 ))
    do 
        cat3=$RANDOM
        let "cat3 %= $cat_max"
    done
    echo $cat1 $cat2 $cat3
    #

    # # get input data using tonic
    python3 transform_DVS_Gesture.py $cat1 $cat2 $cat3 | tee tmp.txt
    cat tmp.txt | grep "^Target\|^Plus\|^Number\|^//\|\.$" | grep -o "[0-9]*$\|/$\|\.$" | tr '\n' ';' | sed "s/\//\/;$s/g" | sed 's/\//\n/g; s/\./\n/g' | sed 's/^;//' | tail +2 >> Results/Simu_$now/Simulation_$now.csv
    rm tmp.txt

    # # get Results
    mkdir Results/Simu_$now/Simu$s
    touch Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    echo "Categories;$cat1;$cat2;$cat3" > Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    echo "Sample times;"`cat data/samples_time.csv` >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    echo "" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    echo "timestamps;neuron tags" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    echo "Samples of categories $cat1, $cat2 and $cat3 have been saved as data/gesture_data.csv\nTimes of the samples have been saved as data/samples_time.csv" 
    
    # matlab command 
    # save_spikeTrain="dlmwrite('Results/Simu_$now/Simu$s/OutputData_Simu$s.csv', OutputData, 'delimiter',';', '-append');"
    save_spikeTrain="data_file=fopen('Results/Simu_$now/Simu$s/OutputData_Simu$s.csv','a');for i=1:length(OutputData); fprintf(data_file, '%d;%d;\n', OutputData(i,:)); end; fclose(data_file);"
    run_plots="addpath('./drawingUtils');run('plot_results.m');saveas(gcf,'Results/Simu_$now/Simu$s/Output_Simu$s.png');close(gcf);"

    # run matlab 
    /usr/local/MATLAB/R2018a/bin/matlab -nosplash -nodesktop -r $import_data$Attention_parameters$Intermediate_parameters$Output_parameters$run_scripts$run_plots$run_accuracy$exit | tee tmp.txt
    
    # save results
    sed -n '/OutputData/,/done/p' tmp.txt | grep '[0-9]' | sed 's/  */;/g' | sed 's/^;//g' >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
    
    # save parameters
    nbActiveOutputNeurons=$(grep "activated Output" tmp.txt | grep -o "[0-9]*")
    rateActiveOutput=$(grep "Percentage of Output layer activation" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rateCoding=$(grep "Accuracy - rate coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rankOrderAccuracy=$(grep "Accuracy - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rankOrderSpecificity=$(grep "Specificity - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    echo "$s;$nbActiveOutputNeurons;$rateActiveOutput;$rateCoding;$rankOrderAccuracy;$rankOrderSpecificity;$thresholdAttention;$tmAttention;$thresholdInter;$tmInter;$nbInterNeurons;$thresholdOutput;$tmOutput;$nbOutputNeurons;" >> Results/Simu_$now/Parameters_Simu_$now.csv
    rm tmp.txt

    echo "Done for simulation loop $s"
    echo ""
    s=$((s+1))
done 