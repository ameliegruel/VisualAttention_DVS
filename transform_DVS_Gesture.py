import os
import tonic 
import tonic.transforms as tr
import numpy as np
import csv

dl = not os.path.isfile('data_gesture/gesture.zip')

gesture = tonic.datasets.DVSGesture(save_to="./data_gesture", download=dl, train=True)
loader = tonic.datasets.DataLoader(gesture, batch_size=1, shuffle=False)
nb=0
for ev,target in iter(loader):
    nb+=1
    print(target)
print(nb)
# ev,target=next(iter(loader))
events = ev.numpy()

print(events.shape)
print(events[0])
print(gesture.sensor_size)
N = np.prod(gesture.sensor_size)
index_x = gesture.ordering.find("x") 
index_y = gesture.ordering.find("y")
index_t = gesture.ordering.find("t")

spikes = []
gesture_data = open("gesture_data.csv","w")
for i in range(N): 
    row = i//(gesture.sensor_size[0])
    col = i%(gesture.sensor_size[1])
    spike_idx = np.where((events[0, :, index_x] == row) & (events[0, :, index_y] == col))[0]
    print(spike_idx)
    spike_times = list(events[0, spike_idx, index_t] * 1e-3) # in milliseconds
    print(spike_times)
    spikes.append(spike_times)
    gesture_data.write(";".join([str(e) for e in spike_times]))
    gesture_data.write(";\n")
        
gesture_data.close()
os.system('csvtool transpose -t ";" -u ";" gesture_data.csv > T_gesture_data.csv')
os.system('mv T_gesture_data.csv gesture_data.csv')

print(np.sum([len(st) for st in spikes]))
idx = ev[0, 0, index_x]*(gesture.sensor_size[0]) + ev[0, 0, index_y] # first spike
print(len(spikes), len(spikes[int(idx)]))  # len(spikes) = 16 384 = 128*128
print(max(sum(spikes, [])))
print(target)
# print(spikes[int(idx)]) 