import os
import tonic 
import tonic.transforms as tr
import numpy as np
import csv
import sys

if len(sys.argv) == 1:
    print("Usage :  python transform_DVS_Gesture.py [category of the sample(s) to load]")
    sys.exit()

dl = not os.path.isfile('data_gesture/gesture.zip')

gesture = tonic.datasets.DVSGesture(save_to="./data_gesture", download=dl, train=True)
loader = tonic.datasets.DataLoader(gesture, batch_size=1, shuffle=False)

print("### Data loaded ###\n")
N = np.prod(gesture.sensor_size)
print("Sensor size du dataset :",gesture.sensor_size)
print("Nombre de pixels :",N)  # len(spikes) = 16384 = 128*128
print()

start_timestamps = 0
spikes = [[] for pixel in range(int(N/4))]
event_by_sample = []
samples_list = [int(sample)+1 for sample in sys.argv[1:]]

for sample in samples_list:
    print("// SAMPLE for category "+str(sample)+" //")
    for ev,target in iter(loader):
        if target.item() == sample and ev.numpy().shape[1] not in event_by_sample: 
            break

    events = ev.numpy()
    print("Target :", target.item())
    print("Number of events :", events.shape[1])
    print("Shape du sample :",events.shape)
    event_by_sample.append(events.shape[1])

    index_x = gesture.ordering.find("x") 
    index_y = gesture.ordering.find("y")
    index_t = gesture.ordering.find("t")

    for pixel in range(int(N/4)): 
        row = pixel // (gesture.sensor_size[0])
        col = pixel %  (gesture.sensor_size[1])
        spike_idx = np.where((events[0, :, index_x]//2 == row) & (events[0, :, index_y]//2 == col))[0]
        spike_times = [start_timestamps + int(round(e)) for e in list(events[0, spike_idx, index_t] * 1e-3)] # in milliseconds
        spikes[pixel] += spike_times

    # print(np.sum([len(st) for st in spikes]))
    # idx = ev[0, 0, index_x]*(gesture.sensor_size[0]) + ev[0, 0, index_y] # first spike
    
    print("Plus grand timestamp :",max(sum(spikes, []))-start_timestamps)
    start_timestamps = max(sum(spikes,[]))
    print("")


print("Writing file...")
gesture_data = open("data/gesture_data.csv","w")
for pixel in spikes:
    gesture_data.write(";".join([str(e) for e in pixel]))
    gesture_data.write(";\n")
gesture_data.close()

os.system('csvtool transpose -t ";" -u ";" data/gesture_data.csv > data/T_gesture_data.csv')
os.system('mv data/T_gesture_data.csv data/gesture_data.csv')
print("Sample(s) have been saved as data/gesture_data.csv")