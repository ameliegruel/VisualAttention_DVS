#!/bin/python 

"""
Bio-inspired visual attention for silicon retinas
Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
From "An Attention-Based Spiking Neural Network for Unsupervised Spike-Sorting" (Bernet et al, 2018)
Run as : $ python Visual_attention.py nest
"""

from pyNN.nest import *
from pyNN.space import *
from pyNN.parameters import Sequence
from pyNN.utility import get_simulator, init_logging, normalized_filename
from pyNN.utility.plotting import DataTable, Figure, Panel
from quantities import ms
import matplotlib.pyplot as plt
import numpy as np
import math
import neo
import datetime

################# CONFIGURE SIMULATOR ############

sim, options = get_simulator(("--plot-figure", "Plot the simulation results to a file", {"action": "store_true"}),
                             ("--fit-curve", "Calculate the best-fit curve to the weight-delta_t measurements", {"action": "store_true"}),
                             ("--attention","Run the network with the attention neuron", {"action": "store_true"}),
                             ("--dendritic-delay-fraction", "What fraction of the total transmission delay is due to dendritic propagation", {"default": 1}),
                             ("--debug", "Print debugging information"))

if options.debug:
    init_logging(None, debug=True)

dt = 1/80000
sim.setup(timestep=0.01)

###############################################  DATA   ########################################################

nSignals = 1
start = 0

# get data from Bernet data.mat 
file_signal = open("data.csv", "r")

file_data = list(map(float, file_signal.readline().split(",")[:50]))
x_input = 10
y_input = math.ceil(max(file_data) - min(file_data))
t_data = len(file_data) - x_input

signal = [[] for i in range(x_input*y_input)]    # setting different spike times for each cell in the population requires an array of array

for t in range(t_data):
    for x in range(x_input):
        y_data = math.floor(file_data[t + x] - min(file_data))
        signal[(y_data-1)*x_input + x].append(t)
signal = [Sequence(signal_1_neuron) for signal_1_neuron in signal]  # more specifically array of inner arrays wrapped in Sequence class (to avoid ambiguities)


############################################### NETWORK #########################################################

# input spikes

Input =  sim.Population(
    x_input*y_input,
    sim.SpikeSourceArray(spike_times=signal),
    label="Input"
)
Input.record("spikes")

# LIF neurons for attention, intermediate and output

if options.attention :
    Attention_parameters = {
        'tau_m': 0.025,     # membrane time constant (in ms)
        'tau_refrac': 0.0,  # duration of refractory period (in ms)
        # 'v_reset': 0.0,     # reset potential after a spike (in mV)
        # 'v_rest': -65.0,    # resting membrane potential (in mV) !
        'v_thresh': -40     # 108.1   # spike threshold (in mV) 
    }
    LIF_Attention = sim.IF_cond_exp(**Attention_parameters)
    Attention = sim.Population(1, LIF_Attention, label="Attention")
    Attention.record("spikes")

Intermediate_parameters = {
    'tau_m': 0.025,     # membrane time constant (in ms)
    'tau_refrac': 0.05, # duration of refractory period (in ms)
    # 'v_reset': 0.0,     # reset potential after a spike (in mV) 
    # 'v_rest': 0.0,      # resting membrane potential (in mV) !
    'v_thresh': -32,    # spike threshold (in mV) 
}
LIF_Intermediate = sim.IF_cond_exp(**Intermediate_parameters)
Intermediate = sim.Population(60, LIF_Intermediate, label="Intermediate")
Intermediate.record(("spikes","v"))

Output_parameters = {
    'tau_m': 3.0,       # membrane time constant (in ms)
    'tau_refrac': 3.0,  # duration of refractory period (in ms)
    'v_thresh': -15      # spike threshold (in mV) !
}
LIF_Output = sim.IF_cond_exp(**Output_parameters)
Output = sim.Population(10, LIF_Output, label="Output")
Output.record("spikes","v")

# connection input to intermediate 

Conn_input_inter = sim.Projection(
    Input, Intermediate,
    connector=sim.AllToAllConnector(allow_self_connections=False),
    synapse_type=sim.StaticSynapse(weight=np.random.uniform(0.4,1, (Input.size, Intermediate.size))),
    receptor_type="excitatory",
    label="Connection input to intermediate"
)

# connection WTA inter

FixedInhibitory_WTA = sim.StaticSynapse(weight=0)
WTA = Projection(
    Intermediate, Intermediate,
    connector=sim.AllToAllConnector(allow_self_connections=False),
    synapse_type=FixedInhibitory_WTA,
    receptor_type="inhibitory",
    label="Connection WTA"
)

# connection inter to output

Conn_inter_output = []

for s in range(3):    # 50 synapses with delay from 1 to 50
    d = 0.05*s
    for action in ["excitatory","inhibitory"]:   # 100 synapses in total between each pre post pairs ? 
        if action == "excitatory":
            w = np.random.uniform(0, 1, (Intermediate.size, Output.size))
            delta_w_pair = 0.05
            delta_w_post = -0.7*delta_w_pair
        elif action == "inhibitory":
            w = np.zeros((Intermediate.size, Output.size))
            delta_w_pair = -0.05
            delta_w_post = -0.1*delta_w_pair

        conn = sim.AllToAllConnector(
            allow_self_connections=False # no autapses
        )

        Conn_inter_output.append( sim.Projection(
            Intermediate, Output,   # pre and post population
            connector=conn,
            synapse_type=sim.StaticSynapse(weight=w),
            receptor_type=action,
            label="Connection intermediate to output"
        )) 


if options.attention : 

    # connection input to attention
    Conn_input_attention = sim.Projection(
        Input, Attention,
        connector=sim.AllToAllConnector(allow_self_connections=False),
        synapse_type=sim.StaticSynapse(weight=10),
        receptor_type="excitatory",
        label="Connection input to attention"
    )

    # connection attention to intermediate
    Conn_attention_inter = sim.Projection(
        Attention, Intermediate,
        connector=sim.AllToAllConnector(allow_self_connections=False),
        synapse_type=sim.StaticSynapse(weight=60),
        receptor_type="",
        label="Connection attention to intermediate"
    )

    # connection attention to output
    Conn_attention_output = sim.Projection(
        Attention, Output,
        connector=sim.AllToAllConnector(allow_self_connections=False),
        synapse_type=sim.StaticSynapse(weight=-10),
        receptor_type="inhibitory",
        label="Connection attention to output"
    )

    # hysteresis connection (attention)
    Hysteresis = sim.Projection(
        Attention, Attention,
        connector=sim.OneToOneConnector(),
        synapse_type=sim.StaticSynapse(weight=10.5),
        receptor_type="excitatory",
        label="Connection attention to output"
    )




################### RUN SIMULATION ####################

"""
*************************************************************************************************
From example "simple_STDP.py" on : http://neuralensemble.org/docs/PyNN/examples/simple_STDP.html
"""

class WeightRecorder(object):
    """
    Recording of weights is not yet built in to PyNN, so therefore we need
    to construct a callback object, which reads the current weights from
    the projection at regular intervals.
    """

    def __init__(self, sampling_interval, projection):
        self.interval = sampling_interval
        self.projection = projection
        self._weights = []

    def __call__(self, t):
        print(t)
        if type(self.projection) != list:
            self._weights.append(self.projection.get('weight', format='list', with_address=False))
        elif type(self.projection) == list:
            for proj in self.projection:
                self._weights.append(proj.get('weight', format='list', with_address=False))
        return t + self.interval

    def get_weights(self):
        signal = neo.AnalogSignal(self._weights, units='nA', sampling_period=self.interval * ms,
                                  name="weight")
        signal.channel_index = neo.ChannelIndex(np.arange(len(self._weights[0])))
        return signal

weight_recorder = WeightRecorder(sampling_interval=1.0, projection=Conn_inter_output)
"""
**************************************************************************************************
"""

class STDP_Input_Inter(object):

    def __init__(self, sampling_interval):
        self.interval = sampling_interval
        self.projection = Conn_input_inter
        self.w = self.projection.get("weight", format="array")
        self.source = Input
        self.target = Intermediate

        # STDP parameters
        self.tau_stdp_minus = 0
        self.tau_stdp_plus = 0.563
        self.delta_w_pair = 0.05
        self.delta_w_post = -5.5*self.delta_w_pair
    
    def __call__(self, t):
        print("input inter start", datetime.datetime.now())
        try : 
            # presynaptic spike times
            t_pre = self.source.get_data().segments[0].spiketrains
            t_pre = [t[-1] if t != [] else 0 for t in t_pre]
            t_pre = np.array([list(t_pre) for i in range(self.target.size)]).T
            
            # postsynaptic spike times
            t_post = self.target.get_data().segments[0].spiketrains
            t_post = [t[-1] if t != [] else 0 for t in t_post]
            t_post = np.array([list(t_post) for i in range(self.source.size)])
            
            delta_t = np.subtract(t_post, t_pre)
            self.w = np.where(t_post > t - 1, self.w+self.delta_w_post, self.w)   # STDP
            self.w = np.where(np.logical_and(np.greater_equal(self.tau_stdp_plus, delta_t), np.greater(delta_t, self.tau_stdp_minus)), self.w+self.delta_w_pair, self.w)
        except IndexError : 
            pass
        self.projection.set(weight=self.w)
        print("input inter stop", datetime.datetime.now())
        return t + self.interval


class STDP_Inter_Output(object):   # ajout thresholding !
    
    def __init__(self, sampling_interval):
        self.interval = sampling_interval
        self.projection = Conn_inter_output
        self.w = [synapse.get("weight", format="array") for synapse in self.projection]
        self.source = Intermediate
        self.target = Output
        self.th = np.array([self.target.get("v_thresh") for n in range(self.target.size)])

        # STDP
        self.tau_stdp_minus = 0.2 # ms
        self.tau_stdp_plus = 3    # ms

        # intrinsic plasticity parameters
        self.tau_ip_minus = 0.2 
        self.tau_ip_plus = 0.3
        self.th_min = -50   # 8
        self.th_max = self.target.get("v_thresh")    # 140
        self.delta_th_post = 0.01
        self.delta_th_pair = 0.6 * self.delta_th_post
        
        # excitatory
        self.delta_w_pair_pos = 0.05
        self.delta_w_post_pos = -0.7*self.delta_w_pair_pos
        
        # inhibitory
        self.delta_w_pair_neg = -0.05
        self.delta_w_post_neg = -0.1*self.delta_w_pair_neg

    def __call__(self,t):
        print("inter output start", datetime.datetime.now())
        for synapse in range(len(self.projection)) : 
            try : 
                # presynaptic spike times
                t_pre = self.source.get_data().segments[0].spiketrains
                t_pre = [t[-1] if t != [] else 0 for t in t_pre]
                t_pre = np.array([list(t_pre) for i in range(self.target.size)]).T

                # postsynaptic spike times
                t_post_target = self.target.get_data().segments[0].spiketrains
                t_post_target = np.array([t[-1] if t != [] else 0 for t in t_post_target])
                t_post_conn = np.array([list(t_post_target) for i in range(self.source.size)])

                delta_t = np.subtract(t_post_conn, t_pre) 
                
                if synapse % 2 == 0:   # excitatory
                    # STDP
                    self.w[synapse] = np.where(t_post_conn > t - 1, self.w[synapse]+self.delta_w_post_pos, self.w[synapse])   
                    self.w[synapse] = np.where(np.logical_and(np.greater_equal(self.tau_stdp_plus, delta_t), np.greater(delta_t, self.tau_stdp_minus)), self.w[synapse]+self.delta_w_pair_pos, self.w[synapse])
                elif synapse % 2 == 1: # inhibitory
                    # STDP
                    self.w[synapse] = np.where(t_post_conn > t - 1, self.w[synapse]+self.delta_w_post_neg, self.w[synapse])
                    self.w[synapse] = np.where(np.logical_and(np.greater_equal(self.tau_stdp_plus, delta_t), np.greater(delta_t, self.tau_stdp_minus)), self.w[synapse]+self.delta_w_pair_neg, self.w[synapse])

                # IP
                self.th = np.where(t_post_target > t - 1, np.max(self.th*self.delta_th_post, self.th_min), self.th)
                increase = np.zeros(self.target.size)
                increase = np.sum(np.where(np.logical_and(np.greater_equal(self.tau_ip_plus, delta_t), np.greater(delta_t, self.tau_ip_minus)), np.min(increase+self.delta_th_pair*self.w[synapse], self.th_max), increase), axis=0)
                self.th = self.th + increase

            except IndexError : 
                pass
            self.projection[synapse].set(weight=self.w[synapse])
            self.target.set(v_thresh=list(self.th))
        print("inter output stop", datetime.datetime.now())
        return t + self.interval


class STP_Input_Attention(object):

    def __init__(self, sampling_interval):
        self.interval = sampling_interval
        self.projection = Conn_input_attention
        self.w = self.projection.get("weight", format="array")
        self.source = Input 
        self.target = Attention
        self.th = np.array([self.target.get("v_thresh") for n in range(self.target.size)])

        # STP
        self.tau_stp = 5 # ms
        self.f_d = 0.0161

    def __call__(self, t):
        print("STP start", datetime.datetime.now())
        try : 
            # presynaptic spike times
            t_pre = self.source.get_data().segments[0].spiketrains
            t_pre = [t[-1] if t != [] else 0 for t in t_pre]
            t_pre = np.array(t_pre).T
            
            # postsynaptic spike times
            t_post = self.target.get_data().segments[0].spiketrains
            t_post = [t[-1] if t != [] else 0 for t in t_post]
            t_post = np.array([list(t_post) for i in range(self.source.size)])
            
            delta_t = np.subtract(t_post, t_pre)
            dirac = np.where(delta_t == 0, 1, 0)
            print(dirac)
            self.w = self.w + (1-self.w)/self.tau_stp - np.sum(self.w * self.f_d * dirac)

        except IndexError : 
            pass
        self.projection.set(weight=self.w)
        print("STP stop", datetime.datetime.now())
        return t + self.interval


class Inhibition_Attention_Output(object):

    def __init__(self, sampling_interval):
        self.interval = sampling_interval
        self.projection = Conn_attention_output
        self.f_inhib = -10
        self.source = Attention
        self.target = Output
        self.v = self.target.get("v_rest")
    
    def __call__(self, t):
        print("Inhibition start", datetime.datetime.now())
        try:
            th = self.target.get("v_thresh")
            print("v",self.v)
            self.v = th * self.f_inhib 
            print("v",self.v)
            self.target.initialize(v=self.v)
        except IndexError: 
            pass
        print("Inhibition stop", datetime.datetime.now())
        return t + self.interval



STDP1 = STDP_Input_Inter(sampling_interval=1.0)
STDP2 = STDP_Inter_Output(sampling_interval=1.0)

if options.attention:
    STP   = STP_Input_Attention(sampling_interval=1.0)
    lateral_inhib = Inhibition_Attention_Output(sampling_interval=1.0)
    sim.run(t_data, callbacks=[weight_recorder, STDP1, STDP2, STP, lateral_inhib])
else : 
    sim.run(t_data, callbacks=[weight_recorder, STDP1, STDP2])

print("SIMULATION DONE")


"""
*************************************************************************************************
From example "simple_STDP.py" on : http://neuralensemble.org/docs/PyNN/examples/simple_STDP.html
adapted to Input-Intermediate synapse
"""
filename = normalized_filename("Results", "Bernet_attention", "pkl", options.simulator)
# Output.write_data(filename, annotations={'script_name': __file__})

Input_data = Input.get_data().segments[0]
print("Input spike times : %s" % Input_data.spiketrains)
Inter_data = Intermediate.get_data().segments[0]
print("Intermediate spike times : %s" % Inter_data.spiketrains)
Output_data = Output.get_data().segments[0]
print("Output spike times: %s" % Output_data.spiketrains)

if options.attention :
    Attention_data = Attention.get_data().segments[0]
    print("Attention spike times : %s" % Attention_data.spiketrains)

weights = weight_recorder.get_weights()
final_weights = np.array(weights[-1])
deltas = dt * np.arange(Input.size*Intermediate.size // 2, -Input.size*Intermediate.size // 2, -1)
print("Final weights: %s" % final_weights)
print("deltas : ", deltas)


if options.fit_curve:
    plasticity_data = DataTable(deltas, final_weights)
    print(len(plasticity_data.x),len(plasticity_data.y))
    print(plasticity_data.x, plasticity_data.y)
    def double_exponential(t, t0, w0, wp, wn, tau):
        return w0 + np.where(t >= t0, wp * np.exp(-(t - t0) / tau), wn * np.exp((t - t0) / tau))
    p0 = (-1.0, 5e-8, 1e-8, -1.2e-8, 20.0)
    popt, pcov = plasticity_data.fit_curve(double_exponential, p0, ftol=1e-10)
    print("Best fit parameters: t0={0}, w0={1}, wp={2}, wn={3}, tau={4}".format(*popt))

if options.plot_figure:
    figure_filename = filename.replace("pkl", "png")
    if options.attention :
        Figure(
            # raster plot of the Input neuron spike times
            Panel(Input_data.spiketrains, ylabel="Input spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            # raster plot of the Inter neuron spike times
            Panel(Inter_data.spiketrains, ylabel="Intermediate spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            # raster plot of the Output neuron spike times
            Panel(Output_data.spiketrains, ylabel="Output spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            
            # raster plot of the Attention neuron spike times
            Panel(Attention_data.spiketrains, ylabel="Attention spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),

            # membrane potential of the postsynaptic neuron
            Panel(Inter_data.filter(name='v')[0], ylabel="Membrane potential (mV)", yticks=True, xlim=(0, t_data), linewidth=0.2),
            
            # evolution of the synaptic weights with time
            Panel(weights, xticks=True, yticks=True, xlabel="Time (ms)", ylabel="Intermediate Output Weight",
                    legend=False, xlim=(0, t_data)),
            # # scatterplot of the final weight of each synapse against the relative
            # # timing of pre- and postsynaptic spikes for that synapse
            # Panel(plasticity_data,
            #         xticks=True, yticks=True, markersize=0.2, xlim=(-Input.size*Intermediate.size / 2 * dt, Input.size*Intermediate.size / 2 * dt),
            #         ylim=(0.9 * final_weights.min(), 1.1 * final_weights.max()),
            #         xlabel="t_post - t_pre (ms)", ylabel="Final weight (nA)"),
            title="Visual attention - Bernet et al. (2018)",
            annotations="Simulated with %s" % options.simulator.upper()
        ).save(figure_filename)
    else : 
        Figure(
            # raster plot of the Input neuron spike times
            Panel(Input_data.spiketrains, ylabel="Input spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            # raster plot of the Inter neuron spike times
            Panel(Inter_data.spiketrains, ylabel="Intermediate spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            # raster plot of the Output neuron spike times
            Panel(Output_data.spiketrains, ylabel="Output spikes", yticks=True, markersize=0.2, xlim=(0, t_data)),
            
            # membrane potential of the postsynaptic neuron
            Panel(Inter_data.filter(name='v')[0], ylabel="Membrane potential (mV)", yticks=True, xlim=(0, t_data), linewidth=0.2),
            
            # evolution of the synaptic weights with time
            Panel(weights, xticks=True, yticks=True, xlabel="Time (ms)", ylabel="Intermediate Output Weight",
                    legend=False, xlim=(0, t_data)),
            # # scatterplot of the final weight of each synapse against the relative
            # # timing of pre- and postsynaptic spikes for that synapse
            # Panel(plasticity_data,
            #         xticks=True, yticks=True, markersize=0.2, xlim=(-Input.size*Intermediate.size / 2 * dt, Input.size*Intermediate.size / 2 * dt),
            #         ylim=(0.9 * final_weights.min(), 1.1 * final_weights.max()),
            #         xlabel="t_post - t_pre (ms)", ylabel="Final weight (nA)"),
            title="Visual attention - Bernet et al. (2018)",
            annotations="Simulated with %s" % options.simulator.upper()
        ).save(figure_filename)

    print(figure_filename)
"""
**************************************************************************************************
"""


sim.end()