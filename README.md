# Visual Attention for Event Cameras based on Spiking Neural Network

This work consists in the re-implemetation of Visual Attention as defined by Bernert and Yvert (2019), using Python and PyNN library. 
On the long term, it is to be applied to pattern recognition on event camera data. 

## How to run the script ? 
Simply use the command : 
`python VisualAttention.py nest --attention --plot-figure`

The arguments are the following : 
- `nest` : defines the SNN simulator to be used by this script. It can be NEST, NEURON, Brian2, etc. Here we used NEST. 
- `--attention` :  if present, the network runs using the attention neuron. Thanks to this neuron, the visual attention takes place. Removing this argument allows you to compare the output of the network without attention. 
- `--plot-figure` : if present, the results are saved in the Results directory in PNG files. 
- `--plot-signal` : if present, the input signal is plot over 50, 100, 1000 and 10000 timesteps and displayed in a Matplotlib window. 

This script runs on Python3 and requires the following libraries to be installed : 
- NEST
- PyNN
- numpy
- matplotlib
- neo
