#!/bin/bash

now=`date +"%F_%H-%M-%S"`
mkdir Results/SimuHyper_$now
touch Results/SimuHyper_$now/Simulation_$now.csv
echo "Simulation loop;Number of active output neurons;Activation rate of output layer;Specific activation rate;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" >> Results/SimuHyper_$now/Simulation_$now.csv

# parameters Attention
thresholdAttention=(25 50 100 108.1 110 125 150 200)  #108.1
tmAttention=(0.2 2 5 10 15 20 50 100 150)             #2

# parameters Inter
thresholdInter=(10 25 50 100 150 200 250 252.7 300)   #article: 252.7 / code: 25
tmInter=(0.000025 0.00025 0.0025 0.025 0.25 2.5 10 25 50 100 150)      #0.025
nbInterNeurons=(60 100 150 200)                       #60

# parameters Output
thresholdOutput=(5 10 14 15 20 25 30 50 100 140)      #article: 140 / code: 25
tmOutput=(0.03 0.3 3 30 100 240 300 500)              #240
nbOutputNeurons=(5 10 11 12 13 14 15 16 17 18 19 20 25 30) 

# define matlab commands
import_data="load('data/gesture_data.mat');samplestime=importdata('data/samples_time.csv');"
run_scripts="run('Attention_Neuron/runScriptDN.m');run('Intermediate_Layer/runScriptL1.m');run('Output_Layer/runScriptL2.m');"
run_accuracy="run('compute_accuracy.m');"
exit="exit;"


s=1
nbSimu=3
# main loops 
while ((s <= nbSimu))
do
    echo "// SIMULATION LOOP $s //"

    # set random variables 
    # tmA=2
    # thA=-25
    # tmI=0.025
    # thI=-25
    # nbI=60
    # tmO=240
    # thO=-25
    # nbO=5

    tmA=${tmAttention[$RANDOM % ${#tmAttention[@]}]}
    thA=${thresholdAttention[$RANDOM % ${#thresholdAttention[@]}]}
    tmI=${tmInter[$RANDOM % ${#tmInter[@]}]}
    thI=${thresholdInter[$RANDOM % ${#thresholdInter[@]}]}
    nbI=${nbInterNeurons[$RANDOM % ${#nbInterNeurons[@]}]}
    tmO=${tmOutput[$RANDOM % ${#tmOutput[@]}]}
    thO=${thresholdOutput[$RANDOM % ${#thresholdOutput[@]}]}
    nbO=${nbOutputNeurons[$RANDOM % ${#nbOutputNeurons[@]}]}

    # define matlab commands
    Attention_parameters="SIMU.DN_tm=$tmA;SIMU.DN_threshold=$thA;"
    Intermediate_parameters="SIMU.L1_tm=$tmI;SIMU.L1_threshold=$thI;SIMU.L1_nNeurons=$nbI;"
    Output_parameters="SIMU.L2_tm=$tmO;SIMU.L2_maxTh=$thO;SIMU.L2_nNeurons=$nbO;"
    run_plots="addpath('./drawingUtils');run('plot_results.m');saveas(gcf,'Results/SimuHyper_$now/HyperSimu$s.png');close(gcf);"

    # matlab
    /usr/local/MATLAB/R2018a/bin/matlab -nosplash -nodesktop -r $import_data$Attention_parameters$Intermediate_parameters$Output_parameters$run_scripts$run_plots$run_accuracy$exit | tee tmp.txt
    
    # fill out csv 
    nbActiveOutputNeurons=$(grep "activated Output" tmp.txt | grep -o "[0-9]*")
    rateActiveOutput=$(grep "Percentage of Output layer activation" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rateCoding=$(grep "Accuracy - rate coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rankOrderAccuracy=$(grep "Accuracy - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    rankOrderSpecificity=$(grep "Specificity - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
    echo "$s;$nbActiveOutputNeurons;$rateActiveOutput;$rateCoding;$rankOrderAccuracy;$rankOrderSpecificity;$thA;$tmA;$thI;$tmI;$nbI;$thO;$tmO;$nbO;" >> Results/SimuHyper_$now/Simulation_$now.csv
    rm tmp.txt

    echo "Done for simulation loop $s"
    echo ""
    s=$((s+1))
done