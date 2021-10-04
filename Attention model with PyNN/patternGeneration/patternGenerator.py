"""
Event-camera like patterns generator
Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
"""

from datetime import datetime
import numpy as np

description=""

def getPoisson1Dpattern(begin, length):
    return np.sort(np.random.poisson(begin+length/2, length))

def getConstant1Dpattern(begin,length):
    return np.arange(begin, begin+length)

def get1Dpattern(begin, length, user):
    nb_sequences = testNumericalInput(input("How many event sequences ? "))
    global description
    description+=str(nb_sequences)+" sequences; for each, "
    events = np.zeros((length*nb_sequences,4))
    events[::,2] = np.ones((length*nb_sequences,))
    
    if user == "A":
        for s in range(nb_sequences):
            events[s*length:length+s*length,3] = getConstant1Dpattern(begin+2*s*length, length)
        description += str(length)+" events starting at "+str(begin+2*s*length)+", with constant timestep of 1 between each event's timestamp;"
    elif user == "B":
        for s in range(nb_sequences):
            events[s*length:length+s*length,3] = getPoisson1Dpattern(begin+2*s*length,length)
        description += "Poisson sequence with l="+str(begin+2*s*length+length/2)+" for "+str(length)+" events;"

    return events


def get2Dpattern(begin, length, nb_pixels):
    events = np.zeros((length,))


def getPattern():
    user=""
    while user not in ["A","B", "C", "D"]:
        user = input("Which type of pattern ? (see patterns.csv) ")
    
    if user in ["A", "B", "C"]:
        size_sequence = testNumericalInput(input("Size of sequence ? "))
        events = get1Dpattern(size_sequence,size_sequence, user)

    events_filename="pattern"+user+"_"+datetime.now().strftime("%Y%m%d_%H%M%S.npy")
    np.save("generatedPatterns/"+events_filename, events)
    describe_file = open("generatedPatterns.csv","a") # adds description to existing file
    describe_file.write(events_filename+";"+description+"\n")
    describe_file.close()

    return events


### ERROR HANDLING ###

def testNumericalInput(user_input):
    while True:
        try : 
            user_input = int(user_input)
            break
        except ValueError :
            user_input = input("Incorrect Value - Please enter a numerical value: ")
    return int(user_input)


### MAIN ###
print(getPattern())