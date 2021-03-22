import os
import tonic 
import tonic.transforms as tr
import numpy as np
import csv
import argparse


# set up PARSER 
parser = argparse.ArgumentParser(description="Import samples from specific categories of DVS128 Gesture and save them as csv")
parser.add_argument("categories", metavar="C", type=int, nargs="+", help="Wanted category, defined by an integer between 1 and 11")
parser.add_argument("--different_samples","-d", help="Get different samples for a specific category called many times (True by default)", action='store_true', default=True)
parser.add_argument("--same_samples","-s", help="Get the same sample for a specific category called many times", action='store_true')
parser.add_argument("--loop","-l", help="Create a csv with same category L times", nargs=1, metavar="L", type=int)
args = parser.parse_args()

print(args)


## FUNCTIONS
def getSpikes(ev, target, spikes, samples_time, start_timestamps):

    events = ev.numpy()
    print("Target :", target.item()+1)
    print("Number of events :", events.shape[1])
    print("Shape du sample :",events.shape)

    index_x = gesture.ordering.find("x") 
    index_y = gesture.ordering.find("y")
    index_t = gesture.ordering.find("t")

    for pixel in range(int(N/4)):   # spatial reduction (each block of 4 pixels will be considered as one pixel)
        row = pixel // (gesture.sensor_size[0])
        col = pixel %  (gesture.sensor_size[1])
        spike_idx = np.where((events[0, :, index_x]//2 == row) & (events[0, :, index_y]//2 == col))[0]   # 
        spike_times = [start_timestamps + int(round(e)) for e in list(events[0, spike_idx, index_t] * 1e-3)] # spatial reduction (each event is rounded to the millisecond)
        spikes[pixel] += spike_times

    # print(np.sum([len(st) for st in spikes]))
    # idx = ev[0, 0, index_x]*(gesture.sensor_size[0]) + ev[0, 0, index_y] # first spike
    
    print("Plus grand timestamp :",max(sum(spikes, []))-start_timestamps)
    start_timestamps = max(sum(spikes,[]))
    samples_time.append(start_timestamps)
    print("")
    return (spikes, samples_time, start_timestamps)


## MAIN

# download and import DVS128 Gesture data
dl = not os.path.isfile('data_gesture/gesture.zip')
gesture = tonic.datasets.DVSGesture(save_to="./data_gesture", download=dl, train=True)
loader = tonic.datasets.DataLoader(gesture, batch_size=1, shuffle=False)

print("### Data loaded ###\n")
N = np.prod(gesture.sensor_size)
print("Sensor size du dataset :",gesture.sensor_size)
print("Nombre de pixels :",N)  # len(spikes) = 16384 = 128*128
print()

# main loop
start_timestamps = 0
spikes = [[] for pixel in range(int(N/4))]
samples_time = []
event_by_sample = []
if args.same_samples:
    args.different_samples = False

if args.loop == None : 
    for category in args.categories:
        print("// SAMPLE for category "+str(category)+" //")

        for ev,target in iter(loader):
            if args.same_samples and target.item() == category-1: 
                break
            if args.different_samples and target.item() == category-1 and ev.numpy().shape[1] not in event_by_sample: 
                event_by_sample.append(ev.numpy().shape[1])
                break

        spikes, samples_time, start_timestamps = getSpikes(ev, target, spikes, samples_time, start_timestamps)

else : 
    category = args.categories[0]
    if args.same_samples :
        for ev,target in iter(loader):
            if target.item() == category-1:
                break
        
        spikes, samples_time, start_timestamps = getSpikes(ev, target, spikes, samples_time, start_timestamps)
        t_max = start_timestamps

        for l in range(args.loop[0]):
            print("// SAMPLE "+str(l+1)+" for category "+str(category))
            for pixel in range(int(N/4)):
                spike_times = [start_timestamps + e for e in spikes[pixel] if e <=t_max] # spatial reduction (each event is rounded to the millisecond)
                spikes[pixel] += spike_times
            start_timestamps = max(sum(spikes,[]))
            samples_time.append(start_timestamps)
            print("")


    elif args.different_samples :
        for l in range(args.loop[0]):
            print("// SAMPLE "+str(l+1)+" for category "+str(category))
        
            for ev,target in iter(loader):
                if target.item() == category-1 and ev.numpy().shape[1] not in event_by_sample:
                    event_by_sample.append(ev.numpy().shape[1])
                    break
            spikes, samples_time, start_timestamps = getSpikes(ev, target, spikes, samples_time, start_timestamps)


# writing data into csv
print("Writing files...")

gesture_data = open("data/gesture_data.csv","w")
for pixel in spikes:
    gesture_data.write(";".join([str(e) for e in pixel]))
    gesture_data.write(";\n")
gesture_data.close()

os.system('csvtool transpose -t ";" -u ";" data/gesture_data.csv > data/T_gesture_data.csv')
os.system('mv data/T_gesture_data.csv data/gesture_data.csv')
print("Sample(s) have been saved as data/gesture_data.csv")

samples_data = open("data/samples_time.csv", "w")
samples_data.write(";".join([str(sample) for sample in samples_time]))
samples_data.close()
print("Times of the sample(s) have been saved as data/samples_time.csv")