#!/bin/bash

now=`date +"%F_%H-%M-%S"`
start=`date +"%s"`
touch Hyperparametrisation/Simulation_$now.csv

# parameters Attention
thresholdAttention=(-60 -55 -50 -45 -40 -35 -30 -25 -20 -15 -10 -5)  #-50
tmAttention=(0.2 2 5 10 15 20 25 40 50)         #25
trAttention=(0.01 0.02 0.05 0.1 0.5 1 2 5)      #0.02

# parameters Intermediate
thresholdInter=(-60 -55 -50 -45 -40 -35 -30 -25 -20 -15 -10 -5)   #-15
tmInter=(0.01 0.02 0.05 0.1 0.5 2 5 10 15 20 25 40 50)         #0.05
trInter=(0.01 0.02 0.05 0.1 0.5 1 2 5)      #0.05

# parameters Output
thresholdOutput=(-60 -55 -50 -45 -40 -35 -30 -25 -20 -15 -10 -5)   #-30
tmOutput=(0.01 0.02 0.03 0.05 0.1 0.5 2 5 10 15 20 25 40 50)         #0.03
trOutput=(0.01 0.02 0.05 0.1 0.2 0.3 0.4 0.5 1 2 5)      #0.3

# parameters connections
w_WTA_inter=(0.2 0.5 0.7 1 2 5 10)         #10
w_input_attention=(0.2 0.5 0.7 1 2 5 10)   #10
w_attention_inter=(0.2 0.5 0.7 1 2 5 10)   #60
w_attention_output=(0.2 0.5 0.7 1 2 5 10)  #5
w_hysteresis=(0.2 0.5 0.7 1 2 5 10)        #1


# input pattern 
events="patternGeneration/generatedPatterns/patternI_20211025_133733.npy"

# Save parameters 
echo "Simulation;Input pattern;Output file name;Computation time;threshold Attention;tm Attention;tau refrac Attention;threshold Intermediate;tm Intermediate;tau refrac Intermediate;threshold Output;tm Output;tau refrac Output;w WTA inter;w input attention;w attention inter;w attention output;w hysteresis;" > Hyperparametrisation/Simulation_$now.csv
# When accuracy run with Random Forest Classifier (Scikit-learn):
# echo "Simulation;Input pattern;Output file name;Computation time;Rate coding;Rank order coding;Latency coding;threshold Attention;tm Attention;tau refrac Attention;threshold Intermediate;tm Intermediate;tau refrac Intermediate;threshold Output;tm Output;tau refrac Output;w WTA inter;w input attention;w attention inter;w attention output;w hysteresis;" > Hyperparametrisation/Simulation_$now.csv

s=1
nbSimu=50
# main loops 
while ((s <= nbSimu))
do
    echo "// SIMULATION $s //"
    
    # set random parameters
    thA=${thresholdAttention[$RANDOM % ${#thresholdAttention[@]}]}
    tmA=${tmAttention[$RANDOM % ${#tmAttention[@]}]}
    trA=${trAttention[$RANDOM % ${#trAttention[@]}]}
    
    thI=${thresholdInter[$RANDOM % ${#thresholdInter[@]}]}
    tmI=${tmInter[$RANDOM % ${#tmInter[@]}]}
    trI=${trInter[$RANDOM % ${#trInter[@]}]}
    
    thO=${thresholdOutput[$RANDOM % ${#thresholdOutput[@]}]}
    tmO=${tmOutput[$RANDOM % ${#tmOutput[@]}]}
    trO=${trOutput[$RANDOM % ${#trOutput[@]}]}

    w1=${w_WTA_inter[$RANDOM % ${#w_WTA_inter[@]}]}
    w2=${w_input_attention[$RANDOM % ${#w_input_attention[@]}]}
    w3=${w_attention_inter[$RANDOM % ${#w_attention_inter[@]}]}
    w4=${w_attention_output[$RANDOM % ${#w_attention_output[@]}]}
    w5=${w_hysteresis[$RANDOM % ${#w_hysteresis[@]}]}
    
    # run network
    python3 VisualAttention.py nest --plot-figure --pattern $events --attention --parameters $thA $tmA $trA $thI $tmI $trI $thO $tmO $trO $w1 $w2 $w3 $w4 $w5  | tee tmp.txt

    # save results
    file_name=`grep "Results/" tmp.txt`
    comput_time=`grep "###" tmp.txt | awk '{print $NF}'`
    rm tmp.txt
    
    echo "$s;$events;$file_name;$comput_time;$thA;$tmA;$trA;$thI;$tmI;$trI;$thO;$tmO;$trO;$w1;$w2;$w3;$w4;$w5" >> Hyperparametrisation/Simulation_$now.csv
    # When accuracy run with Random Forest Classifier (Scikit-learn):
        # rateCodingAccuracy=$(grep "Rate" tmp.txt | grep -o "[0-9]\.[0-9]*")
        # rankOrderCodingAccuracy=$(grep "Rank" tmp.txt | grep -o "[0-9]\.[0-9]*")
        # latencyCodingAccuracy=$(grep "Latency" tmp.txt | grep -o "[0-9]\.[0-9]*")
        # echo "$s;$rateCodingAccuracy;$rankOrderCodingAccuracy;$latencyCodingAccuracy;$thA;$tmA;$thI;$tmI;$nbI;$thO;$tmO;$nbO;" >> Results/HyperSimu_$now/Parameters_Simu_$now.csv

    echo ""
    s=$((s+1))
done

end_sim=`date +"%s"`

echo "Simulation complète en" $((end_sim-start)) "secondes"