import os
import tonic 
import tonic.transforms as tr
import numpy as np
import csv
from skimage.measure import block_reduce

dl = not os.path.isfile('data_gesture/gesture.zip')

gesture = tonic.datasets.DVSGesture(save_to="./data_gesture", download=dl, train=True)
loader = tonic.datasets.DataLoader(gesture, batch_size=1, shuffle=False)
"""
nb=0
for ev,target in iter(loader):
    nb+=1
    print(target)
print(nb)
"""
ev,target=next(iter(loader))
print("Target :", target)
events = ev.numpy()

print("Shape du sample :",events.shape)
print("Sensor size du dataset :",gesture.sensor_size)
N = np.prod(gesture.sensor_size)
index_x = gesture.ordering.find("x") 
index_y = gesture.ordering.find("y")
index_t = gesture.ordering.find("t")

spikes = []
gesture_data = open("data/gesture_data.csv","w")
for i in range(int(N/4)): 
    row = i // (gesture.sensor_size[0])
    col = i %  (gesture.sensor_size[1])
    spike_idx = np.where((events[0, :, index_x]//2 == row) & (events[0, :, index_y]//2 == col))[0]
    spike_times = [int(round(e)) for e in list(events[0, spike_idx, index_t] * 1e-3)] # in milliseconds
    spikes.append(spike_times)
    gesture_data.write(";".join([str(e) for e in spike_times]))
    gesture_data.write(";\n")

gesture_data.close()
os.system('csvtool transpose -t ";" -u ";" data/gesture_data.csv > data/T_gesture_data.csv')
os.system('mv data/T_gesture_data.csv data/gesture_data.csv')

print(np.sum([len(st) for st in spikes]))
# idx = ev[0, 0, index_x]*(gesture.sensor_size[0]) + ev[0, 0, index_y] # first spike
print("Nombre de pixels :",len(spikes))  # len(spikes) = 16384 = 128*128
print("Plus grand timestamp :",max(sum(spikes, [])))
