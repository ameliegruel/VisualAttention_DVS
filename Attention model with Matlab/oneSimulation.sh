#!/bin/bash

now=`date +"%F_%T"`
start=`date +"%s"`
mkdir Results/Simu_$now/
touch Results/Simu_$now/Simulation_$now.csv
echo "Simulation loop;Category;Sample;Bigger timestamp;" >> Results/Simu_$now/Simulation_$now.csv

# parameters Attention
thresholdAttention=25
tmAttention=2

# parameters Inter
thresholdInter=-15
tmInter=0.025
nbInterNeurons=60

# parameters Output
thresholdOutput=-15
tmOutput=240
nbOutputNeurons=11

# save parameters
touch Results/Simu_$now/Parameters_Simu_$now.csv
echo "Simulation;Simulation loop;Number of active output neurons;Activation rate of output layer;Rate coding;Rank order coding - Accuracy;Rank order coding - Specificity;threshold Attention;tm Attention;threshold Intermediate;tm Intermediate;neurons Intermediate;threshold Output;tm Output;neurons Output;" > Results/Simu_$now/Parameters_Simu_$now.csv

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

categories=""
for c in ${cats[@]} 
do 
    l=0
    while ((l < loop))
    do 
        categories=$categories$c";"
        l=$((l+1))
    done
done

mkdir Results/Simu_$now/Simu$s
touch Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
echo "Categories;;$categories" > Results/Simu_$now/Simu$s/OutputData_Simu$s.csv

# get input data using tonic
start=`date +"%s"`
python3 getDVS128Gesture.py $@ | tee tmp.txt
fin=`date +"%s"`
cat tmp.txt | grep "^$\|Bigger\|Sample:\|//" | sed 's/^$/?/g' | grep -o "[0-9]*\|?" | tr '\n' ';' | sed 's/?/\n$s/g' >> Results/Simu_$now/Simulation_$now.csv
rm tmp.txt

echo "Sample times;"`cat data/samples_time.csv` >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
echo "" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
echo "timestamps;neuron tags" >> Results/Simu_$now/Simu$s/OutputData_Simu$s.csv
echo "Samples of categories $cats have been saved as data/gesture_data.csv"
echo "Times of the samples have been saved as data/samples_time.csv" 
#

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

echo "Simulation done"
end=`date +"%s"`

echo "Récupération des données en" $(($fin-$start)) "secondes"
echo "Simulation complète en" $(($end-$start)) "secondes"