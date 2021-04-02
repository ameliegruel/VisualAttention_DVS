import os
import tonic 
import tonic.transforms as tr
import numpy as np
# download and import DVS128 Gesture data
dl = not os.path.isfile('data_gesture/gesture.zip')
gesture = tonic.datasets.DVSGesture(save_to="./data_gesture", download=dl, train=True)
loader = tonic.datasets.DataLoader(gesture, batch_size=1, shuffle=False)

print("### Data loaded ###\n")
N = np.prod(gesture.sensor_size)
print("Sensor size du dataset :",gesture.sensor_size)
print("Nombre de pixels :",N,"\n")  # len(spikes) = 16384 = 128*128

def getSpikes(ev, target):

    events = ev.numpy()
    print("Target :", target.item()+1)
    print("Number of events :", events.shape[1])
    print("Shape du sample :",events.shape)

    index_x = gesture.ordering.find("x") 
    index_y = gesture.ordering.find("y")
    index_t = gesture.ordering.find("t")
    spikes = [[] for pixel in range(int(N/4))]

    for pixel in range(int(N/4)):   # spatial reduction (each block of 4 pixels will be considered as one pixel)
        row = pixel // (gesture.sensor_size[0])
        col = pixel %  (gesture.sensor_size[1])
        spike_idx = np.where((events[0, :, index_x]//2 == row) & (events[0, :, index_y]//2 == col))[0]   # 
        spike_times = [int(round(e)) for e in list(events[0, spike_idx, index_t] * 1e-3)] # spatial reduction (each event is rounded to the millisecond)
        spikes[pixel] += spike_times

    max_time = max(sum(spikes,[]))
    print("Plus grand timestamp :",max_time,"\n")
    return (spikes, max_time)


# main loop
categories = {"Category "+str(c):0 for c in range(1,12)}
length_data = open("DVS128_data/samples_length.csv", "w")

for ev,target in iter(loader):
    print(target.item()+1)
    categories["Category "+str(target.item()+1)] += 1

    # get data 
    print("Category "+str(target.item()+1)+" - sample "+str(categories["Category "+str(target.item()+1)]))
    spikes, max_length = getSpikes(ev, target)
    length_data.write("Category"+str(target.item()+1)+"_Sample"+str(categories["Category "+str(target.item()+1)])+";"+str(max_length)+";\n")

    # writing data into csv
    gesture_data = open("DVS128_data/Category"+str(target.item()+1)+"_Sample"+str(categories["Category "+str(target.item()+1)])+".csv","w")
    for pixel in spikes:
        gesture_data.write(";".join([str(e) for e in pixel]))
        gesture_data.write(";\n")
    gesture_data.close()

length_data.close()