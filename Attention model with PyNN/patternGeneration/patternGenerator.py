"""
Event-camera like patterns generator
Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
"""

from datetime import datetime
import numpy as np
from numpy.core.fromnumeric import size

description=""

def getEmpty1Dpattern(begin_ts, length):    # returns the new beginning timestamps after a certain delay with no events
    return begin_ts+length+1

def getPoisson1Dpattern(begin_ts, length):
    pattern = np.zeros((length, 4))
    pattern[::,3] = np.sort(np.random.poisson(begin_ts+length/2, length))
    return pattern, pattern[-1,3]+1

def getConstant1Dpattern(begin_ts,length):
    pattern = np.zeros((length,4))
    pattern[::,3] = np.arange(begin_ts, begin_ts+length)
    return pattern, begin_ts+length

def morse2events(letter, timestamp):
    pattern = np.zeros((len(letter), 4))
    pattern[::,2] = 1
    e=0
    for s in letter : 
        pattern[e,3]=timestamp
        if s=="." :
            timestamp+=1   # a '.' corresponds to 1 event during over 1 timestep
        elif s=="_":
            timestamp+=3   # a '_' corresponds to 1 event during over 3 timesteps
        e+=1
    return pattern, timestamp+1


def getMorse1Dpattern(begin_ts, letter=None):
    morseCode = {
        "A": "._",
        "B": "_...",
        "C": "_._.",
        "D": "_..",
        "E": ".",
        "F": ".._.",
        "G": "__.",
        "H": "....",
        "I": "..",
        "J": ".___",
        "K": "_._",
        "L": "._..",
        "M": "__",
        "N": "_.",
        "O": "___",
        "P": ".__.",
        "Q": "__._",
        "R": "._.",
        "S": "...",
        "T": "_",
        "U": ".._",
        "V": "..._",
        "W": ".__",
        "X": "_.._",
        "Y": "_.__",
        "Z": "__..",
        "0": "_____",
        "1": ".____",
        "2": "..___",
        "3": "...__",
        "4": "...._",
        "5": ".....",
        "6": "_....",
        "7": "__...",
        "8": "___..",
        "9": "____."
    }
    events = np.zeros((0,4))
    if letter==None:
        global description
        while True:
            letter = input("Which letter/number to include in the pattern ? (A to Z, 0 to 9) ")
            try :
                pattern, begin_ts = morse2events(morseCode[letter],begin_ts)
                events=np.concatenate((events, pattern), axis=0)
                description+=letter
            except KeyError:
                break
        description+=";"
    else : 
        pattern, begin_ts = morse2events(morseCode[letter],begin_ts)
        events=np.concatenate((events, pattern), axis=0)
    return events, begin_ts


def get1Dpattern(user, length_pattern=None, length_empty=None, nb_sequences=None):
    global description
    
    events = np.zeros((0,4))
    begin_ts = 0
    
    if user == "A":
        description += str(length_pattern)+" events with constant timestep of 1 between each event's timestamp;"
        for _ in range(nb_sequences):
            begin_ts = getEmpty1Dpattern(begin_ts, length_empty)
            pattern, begin_ts = getConstant1Dpattern(begin_ts, length_pattern)
            events = np.concatenate((events, pattern), axis=0)

    elif user == "B":
        description += "Poisson sequence with l="+str(begin_ts+length_pattern/2)+" for "+str(length_pattern)+" events;"
        for _ in range(nb_sequences):
            begin_ts = getEmpty1Dpattern(begin_ts, length_empty)
            pattern, begin_ts = getPoisson1Dpattern(begin_ts, length_pattern)
            events = np.concatenate((events, pattern), axis=0)

    elif user == "C":
        description += "Succession of different letters in Morse code, following the pattern "
        pattern, begin_ts = getMorse1Dpattern(begin_ts)
        events = np.concatenate((events, pattern), axis=0)

    elif user == "D":
        letter = input("Which letter/number ? ")
        nb_letter = testNumericalInput(input("How many time the same letter "+letter+" ? "))
        description += str(nb_letter)+" repetitions of the same letter "+letter+" in Morse code;"
        pattern, pattern_begin_ts = getMorse1Dpattern(begin_ts, letter)
        for _ in range(nb_letter-1):
            pattern = np.concatenate((pattern, np.vectorize(lambda x: x+pattern_begin_ts if x>0 else x)(pattern)), axis=0)
        for _ in range(nb_sequences):
            begin_ts=getEmpty1Dpattern(begin_ts, length_empty)
            events = np.concatenate((events, np.vectorize(lambda x: x+begin_ts if x>0 else x)(pattern)), axis=0)
            begin_ts += pattern_begin_ts
    
    elif user == "E":
        description += "Succession of different letters in Morse code, following the pattern "
        pattern, pattern_begin_ts = getMorse1Dpattern(begin_ts)
        for _ in range(nb_sequences):
            begin_ts=getEmpty1Dpattern(begin_ts, length_empty)
            events = np.concatenate((events, np.vectorize(lambda x: x+begin_ts if x>0 else x)(pattern)), axis=0)
            begin_ts += pattern_begin_ts


    return events


def get2Dpattern(begin_ts, length, nb_pixels):
    events = np.zeros((length,))


def getPattern():
    global description
    user = size_sequence = size_empty = nb_sequences = None
    
    while user not in ["A","B","C","D","E"]:
        user = input("Which type of pattern ? (see patterns.csv) ")
    
    if user in ["A","B"]:
        size_sequence = testNumericalInput(input("Size of sequence ? "))
    if user in ["A", "B", "D","E"]: 
        size_empty = testNumericalInput(input("How long without events between the patterns/event sequences ? "))
        nb_sequences = testNumericalInput(input("How many event sequences ? "))
        description+=str(nb_sequences)+" sequences, separated by "+str(size_empty)+" timesteps;"
        
    events = get1Dpattern(user,length_pattern=size_sequence, length_empty=size_empty, nb_sequences=nb_sequences)
    events[::,2] = 1

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

print(getPattern())