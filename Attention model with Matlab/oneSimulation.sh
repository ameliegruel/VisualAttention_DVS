#!/bin/bash

now=`date +"%F_%H-%M-%S"`
start=`date +"%s"`
# mkdir Results/Simu_$now/
# touch Results/Simu_$now/Simulation_$now.csv
# echo "Simulation;Video;Category;Sample;Bigger timestamp;" >> Results/Simu_$now/Simulation_$now.csv

# parameters Attention
thresholdAttention=12
tmAttention=25

# parameters Inter
thresholdInter=12
tmInter=25
nbInterNeurons=60

# parameters Output
thresholdOutput=12
tmOutput=25
nbOutputNeurons=11

# save parameters
# touch Results/Simu_$now/Parameters_Simu_$now.csv
# echo "Simulation;Number of active output neurons;Activation rate of output layer;Rate coding;Rank order coding - Accuracy;Rank order coding - Specificity;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" > Results/Simu_$now/Parameters_Simu_$now.csv

# define matlab commands 
import_data="gesturedata=importdata('data/gesture_data.csv');samplestime=importdata('data/samples_time.csv');save('data/gesture_data.mat','gesturedata','-v7.3');"
Attention_parameters="SIMU.DN_tm=$tmAttention;SIMU.DN_threshold=$thresholdAttention;"
Intermediate_parameters="SIMU.L1_tm=$tmInter;SIMU.L1_threshold=$thresholdInter;SIMU.L1_nNeurons=$nbInterNeurons;"
Output_parameters="SIMU.L2_tm=$tmOutput;SIMU.L2_maxTh=$thresholdOutput;SIMU.L2_nNeurons=$nbOutputNeurons;"
run_scripts="run('Attention_Neuron/runScriptDN.m');run('Intermediate_Layer/runScriptL1.m');run('Output_Layer/runScriptL2.m');"
run_accuracy="run('compute_accuracy.m');"
exit="exit;"


# SIMULATION
echo "Start simulation"
s=1

# get categories
echo "Categories: $@"  # use all parameters given as input, as categories to test

arg_cat=true
cats=""
arg_loop=false
loop=1
for arg in "$@"
do 
    if [[ "$arg" == "-l" ]]
    then
        arg_cat=false
        arg_loop=true
    elif [[ "$arg_cat" == true && $arg =~ ^[0-9]+$ ]]
    then
        cats=$cats$arg" "
    elif [[ "$arg_loop" == true && $arg =~ ^[0-9]+$ ]]
    then
        loop=$arg
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
echo "simu param: $simu_parameters"

# mkdir Results/Simu_$now/Simu$s
# touch Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
# echo "Categories;;$categories" > Results/Simu_$now/Simu$s/OutputData_Simu$s.csv

# get input data using tonic
start=`date +"%s"`
python3 getDVS128Gesture.py $@ | tee tmp.txt
fin=`date +"%s"`
# cat tmp.txt | grep "^$\|Bigger\|Sample:\|//" | sed 's/^$/?/g' | sed "s/\/\//$s/g" | grep -o '[0-9]*\|?' | tr '\n' ';' | sed "s/?;/\n/g" >> Results/Simu_$now/Simulation_$now.csv
# rm tmp.txt

# echo "Sample times;"`cat data/samples_time.csv` >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
# echo "" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
# echo "timestamps;neuron tags" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
#

# matlab command 
# run_plots="addpath('./drawingUtils');run('plot_results.m');saveas(gcf,'Results/Simu_$now/Simu$s/Output_Simu$s.png');close(gcf);"
run_plots="addpath('./drawingUtils');run('plot_results.m');close(gcf);"

# run matlab 
/usr/local/MATLAB/R2018a/bin/matlab -nosplash -nodesktop -r $import_data$simu_parameters$Attention_parameters$Intermediate_parameters$Output_parameters$run_scripts$run_plots$run_accuracy$exit #| tee tmp.txt

# save results
# sed -n '/OutputData/,/done/p' tmp.txt | grep '[0-9]' | sed 's/  */;/g' | sed 's/^;//g' >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv

# save parameters
# nbActiveOutputNeurons=$(grep "activated Output" tmp.txt | grep -o "[0-9]*")
# rateActiveOutput=$(grep "Percentage of Output layer activation" tmp.txt | grep -o "[0-9]\.*[0-9]*")
# rateCoding=$(grep "Accuracy - rate coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
# rankOrderAccuracy=$(grep "Accuracy - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
# rankOrderSpecificity=$(grep "Specificity - rank order coding" tmp.txt | grep -o "[0-9]\.*[0-9]*")
# echo "$s;$nbActiveOutputNeurons;$rateActiveOutput;$rateCoding;$rankOrderAccuracy;$rankOrderSpecificity;$thresholdAttention;$tmAttention;$thresholdInter;$tmInter;$nbInterNeurons;$thresholdOutput;$tmOutput;$nbOutputNeurons;" >> Results/Simu_$now/Parameters_Simu_$now.csv
# rm tmp.txt

echo "Simulation done"
end_sim=`date +"%s"`

echo "Récupération des données en" $(($fin-$start)) "secondes"
echo "Simulation complète en" $(($end_sim-$start)) "secondes"