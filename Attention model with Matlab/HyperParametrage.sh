#!/bin/bash

now=`date +"%F_%H-%M-%S"`
start=`date +"%s"`
mkdir Results/HyperSimu_$now
touch Results/HyperSimu_$now/Simulation_$now.csv
echo "Simulation;Video;Category;Sample;Bigger timestamp;" >> Results/HyperSimu_$now/Simulation_$now.csv

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

# save parameters
touch Results/HyperSimu_$now/Parameters_Simu_$now.csv
# When accuracy run with Matlab script: 
#   echo "Simulation;Number of active output neurons;Activation rate of output layer;Rate coding;Rank order coding - Accuracy;Rank order coding - Specificity;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" > Results/HyperSimu_$now/Parameters_Simu_$now.csv

# When accuracy run with Random Forest Classifier (Scikit-learn):
echo "Simulation;Rate coding;Rank order coding;Latency coding;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" > Results/HyperSimu_$now/Parameters_Simu_$now.csv


# define matlab commands
import_data="gesturedata=importdata('data/gesture_data.csv');samplestime=importdata('data/samples_time.csv');save('data/gesture_data.mat','gesturedata','-v7.3');"
run_scripts="run('Attention_Neuron/runScriptDN.m');run('Intermediate_Layer/runScriptL1.m');run('Output_Layer/runScriptL2.m');"
run_accuracy="" # "run('compute_accuracy.m');"
exit="exit;"


# get categories 
echo "Categories: $@"  # use all parameters given as input, as categories to test

arg_cat=true
cats=""
arg_loop=false
loop=1
arg_simu=false
nbSimu=3
for arg in "$@"
do 
    if [[ "$arg" == "-l" ]]
    then
        arg_cat=false
        arg_simu=false
        arg_loop=true
    elif [[ "$arg" == "-hp" ]]
    then
        arg_cat=false
        arg_loop=false
        arg_simu=true    
    elif [[ "$arg_cat" == true && $arg =~ ^[0-9]+$ ]]
    then
        cats=$cats$arg" "
    elif [[ "$arg_loop" == true && $arg =~ ^[0-9]+$ ]]
    then
        loop=$arg
    elif [[ "$arg_simu" == true && $arg =~ ^[0-9]+$ ]]
    then
        nbSimu=$arg
    fi
done 
echo "Categories:" $cats "over" $loop "loop(s)"
simu_parameters=""

categories=""
nbcat=0
for c in ${cats[@]} 
do 
    nbcat=$((nbcat+1))
    simu_parameters=$simu_parameters"SIMU.cat$nbcat=$c;"
    l=0
    while ((l < loop))
    do 
        categories=$categories$c";"
        l=$((l+1))
    done
done

simu_parameters=$simu_parameters"SIMU.nb_categories=$nbcat;"

# get input data using tonic
start=`date +"%s"`
python3 getDVS128Gesture.py $@ | tee tmp.txt
fin=`date +"%s"`
cat tmp.txt | grep "^$\|Bigger\|Sample:\|//" | sed 's/^$/?/g' | sed "s/\/\//1/g" | grep -o '[0-9]*\|?' | tr '\n' ';' | sed "s/?;/\n/g" >> Results/HyperSimu_$now/Simulation_$now.csv
rm tmp.txt
#


s=1
# main loops 
while ((s <= nbSimu))
do
    echo "// SIMULATION LOOP $s //"
    
    # save data
    mkdir Results/HyperSimu_$now/HyperSimu$s
    touch Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv
    echo "Categories;;$categories" > Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv

    echo "Sample times;"`cat data/samples_time.csv` >> Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv
    echo "" >> Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv
    echo "timestamps;neuron tags" >> Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv

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
    run_plots="addpath('./drawingUtils');run('plot_results.m');saveas(gcf,'Results/HyperSimu_$now/HyperSimu$s/Output_HyperSimu$s.png');saveas(gcf,'Results/HyperSimu_$now/HyperSimu$s/Output_HyperSimu$s.fig');close(gcf);"

    # matlab
    /usr/local/MATLAB/R2018a/bin/matlab -nosplash -nodesktop -r $import_data$simu_parameters$Attention_parameters$Intermediate_parameters$Output_parameters$run_scripts$run_plots$run_accuracy$exit | tee tmp.txt
    
    # save results
    sed -n '/OutputData/,/done/p' tmp.txt | grep '[0-9]' | sed 's/  */;/g' | sed 's/^;//g' >> Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv
    rm tmp.txt

    # get accuracy and save parameters 
    python3 getAccuracy.py Results/HyperSimu_$now/HyperSimu$s/OutputData_Simu$s.csv | tee tmp.txt

    # When accuracy run with Matlab script:
        # nbActiveOutputNeurons=$(grep "activated Output" tmp.txt | grep -o "[0-9]*")
        # rateActiveOutput=$(grep "Percentage of Output layer activation" tmp.txt | grep -o "[0-9]\.*[0-9]*")
        # rateCoding=$(grep "Accuracy - rate coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
        # rankOrderAccuracy=$(grep "Accuracy - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
        # rankOrderSpecificity=$(grep "Specificity - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
        # echo "$s;$nbActiveOutputNeurons;$rateActiveOutput;$rateCoding;$rankOrderAccuracy;$rankOrderSpecificity;$thA;$tmA;$thI;$tmI;$nbI;$thO;$tmO;$nbO;" >> Results/HyperSimu_$now/Parameters_Simu_$now.csv
    
    # When accuracy run with Random Forest Classifier (Scikit-learn):
    rateCodingAccuracy=$(grep "Rate" tmp.txt | grep -o "[0-9]\.[0-9]*")
    rankOrderCodingAccuracy=$(grep "Rank" tmp.txt | grep -o "[0-9]\.[0-9]*")
    latencyCodingAccuracy=$(grep "Latency" tmp.txt | grep -o "[0-9]\.[0-9]*")
    echo "$s;$rateCodingAccuracy;$rankOrderCodingAccuracy;$latencyCodingAccuracy;$thresholdAttention;$tmAttention;$thresholdInter;$tmInter;$nbInterNeurons;$thresholdOutput;$tmOutput;$nbOutputNeurons;" >> Results/HyperSimu_$now/Parameters_Simu_$now.csv

    rm tmp.txt

    echo "Done for simulation loop $s"
    echo ""
    s=$((s+1))
done

end_sim=`date +"%s"`

echo "Récupération des données en" $(($fin-$start)) "secondes"
echo "Simulation complète en" $(($end_sim-$start)) "secondes"