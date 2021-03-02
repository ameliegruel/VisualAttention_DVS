#!/bin/bash

now=`date +"%F_%T"`
mkdir Results/Simu_$now
touch Results/Simu_$now/Simulation_$now.csv
echo "Simulation loop;Category;Number of events;Bigger timestamp;" >> Results/Simu_$now/Simulation_$now.csv

for i in {1..10}
do 
    echo "// SIMULATION LOOP $i //"
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
    echo $cat1 $cat2
    
    python3 transform_DVS_Gesture.py $cat1 $cat1 $cat1 $cat1 $cat1 $cat2 > tmp.txt
    cat tmp.txt | grep "^Target\|^Plus\|^Number\|^//\|\.$" | grep -o "[0-9]*$\|/$\|\.$" | tr '\n' ';' | sed "s/\//\/;$i/g" | sed 's/\//\n/g; s/\./\n/g' | sed 's/^;//' | tail +2 >> Results/Simu_$now/Simulation_$now.csv
    rm tmp.txt

    /usr/local/MATLAB/R2018a/bin/matlab -nosplash -nodesktop -r "gesturedata=importdata('data/gesture_data.csv');save('data/gesture_data.mat','gesturedata');run('Attention_Neuron/runScriptDN.m');run('Intermediate_Layer/runScriptL1.m');run('Output_Layer/runScriptL2.m');addpath('./drawingUtils');run('plot_results.m');saveas(gcf,'Results/Simu_$now/Auto$i-3cat$cat1-2cat$cat2.fig');close(gcf);exit;"
    echo "Done for simulation loop $i\n"
done 