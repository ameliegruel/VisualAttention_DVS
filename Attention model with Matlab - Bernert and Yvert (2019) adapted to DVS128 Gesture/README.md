# Visual Attention for Event Cameras based on Spiking Neural Networks

This work consists in the adaptation of the Matlab code produced by Bernert and Yvert (2019) to the DVS128 Gesture dataset. 
The data is imported from the Python library `tonic` and translated in a CSV file comprehensible by the Matlab code thanks to the script `transform_DVS_Gesture.py`.

## How to run the script ? 

### To run it manually 

1) Import one or more random samples from specific categories of DVS128 Gesture dataset using tonic by running the command line :
   `transform_DVS_Gesture.py cat1 cat2 etc`  
   The arguments cat1, cat2, etc specify the categories to import. 
   If a category is specified more than one time, tonic will import different samples from this category.
2) Launch Matlab, then run successively the scripts : 
   `Attention_Neuron/mexScript.m`
   `Attention_Neuron/runScriptDN.m`
   `Intermediate_Layer/mexScript.m`
   `Intermediate_Layer/runScriptL1.m`
   `Output_Layer/mexScript.m`
   `Output_Layer/runScriptL2.m`
3) To display the results, add the **drawingUtils** directory to the current path then run `plot_results.m`

### To run it manually over many simulations


  
## Requirements
  
`Matlab` should be installed under the version 2018b at least. 
The script `transform_DVS_Gesture.py` requires the following Python libraries : 
- numpy
- csv
- tonic

## Preliminary results
Some preliminary results can be found in the **Results** directory. The format `.fig` can be opened using Matlab. 
