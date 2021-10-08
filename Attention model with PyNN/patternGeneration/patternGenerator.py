"""
Event-camera like patterns generator
Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
"""

from datetime import datetime
import numpy as np
from numpy.core.fromnumeric import size

description=""


### 1D PATTERNS ###

def getEmptyPattern(begin_ts, length):    # returns the new beginning timestamps after a certain delay with no events
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
    return pattern, timestamp


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
            begin_ts = getEmptyPattern(begin_ts, length_empty)
            pattern, begin_ts = getConstant1Dpattern(begin_ts, length_pattern)
            events = np.concatenate((events, pattern), axis=0)

    elif user == "B":
        description += "Poisson sequence with l="+str(begin_ts+length_pattern/2)+" for "+str(length_pattern)+" events;"
        for _ in range(nb_sequences):
            begin_ts = getEmptyPattern(begin_ts, length_empty)
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
        full_pattern = np.zeros((0,4))
        pattern_begin_ts = begin_ts
        
        for _ in range(nb_letter):
            pattern, pattern_begin_ts = getMorse1Dpattern(pattern_begin_ts, letter)
            full_pattern = np.concatenate((full_pattern, pattern), axis=0)

        for _ in range(nb_sequences):
            begin_ts=getEmptyPattern(begin_ts, length_empty)
            events = np.concatenate((events, np.concatenate((full_pattern[::,:3], full_pattern[::,3:]+begin_ts), axis=1) ), axis=0)
            begin_ts += pattern_begin_ts
 
    elif user == "E":
        description += "Succession of different letters in Morse code, following the pattern "
        pattern, pattern_begin_ts = getMorse1Dpattern(begin_ts)    # easier to compute the succession of Morse code this way 
        for _ in range(nb_sequences):
            begin_ts=getEmptyPattern(begin_ts, length_empty) - 1 # to compensate for the pattern_begin_ts adding 1 to begin_ts
            events = np.concatenate((events, np.concatenate((pattern[::,:3], pattern[::,3:]+begin_ts), axis=1) ), axis=0)
            begin_ts += pattern_begin_ts   # to compensate for the pattern_begin_ts adding 1 to begin_rs

    return events


### 2D PATTERNS ###

def get2x2CardinalPattern(): 
    pass

def mvmtN():
    x_coord = []
    y_coord = []
    timestamps = []
    c = 0
    for ts in [3,2,1]:
        x_coord += list(range(3))
        y_coord += [c]*3
        c+=1
        timestamps += [ts]*3
    return x_coord, y_coord, timestamps

def mvmtNE():
    x_coord = []
    y_coord = []
    timestamps = []
    begin = 1
    end = 4
    for x in range(3) :
        x_coord += [x]*3
        y_coord += list(range(2,-1,-1))
        timestamps += list(range(begin,end))
        begin += 1
        end += 1
    return x_coord, y_coord, timestamps

def mvmtE():
    x_coord = []
    y_coord = []
    timestamps = []
    c = 0
    for ts in [1,2,3]:
        x_coord += [c]*3
        y_coord += list(range(3))
        c+=1
        timestamps += [ts]*3
    return x_coord, y_coord, timestamps

def mvmtSE():
    x_coord = []
    y_coord = []
    timestamps = []
    begin = 1
    end = 4
    for x in range(3) :
        x_coord += [x]*3
        y_coord += list(range(3))
        timestamps += list(range(begin,end))
        begin += 1
        end += 1
    return x_coord, y_coord, timestamps

def mvmtS():
    x_coord = []
    y_coord = []
    timestamps = []
    c = 0
    for ts in [1,2,3]:
        x_coord += list(range(3))
        y_coord += [c]*3
        c+=1
        timestamps += [ts]*3
    return x_coord, y_coord, timestamps

def mvmtSW():
    x_coord = []
    y_coord = []
    timestamps = []
    begin = 1
    end = 4
    for x in range(2,-1,-1) :
        x_coord += [x]*3
        y_coord += list(range(3))
        timestamps += list(range(begin,end))
        begin += 1
        end += 1
    return x_coord, y_coord, timestamps

def mvmtW():
    x_coord = []
    y_coord = []
    timestamps = []
    c = 0
    for ts in [3,2,1]:
        x_coord += [c]*3
        y_coord += list(range(3))
        c+=1
        timestamps += [ts]*3
    return x_coord, y_coord, timestamps

def mvmtNW():
    x_coord = []
    y_coord = []
    timestamps = []
    begin = 1
    end = 4
    for x in range(2,-1,-1) :
        x_coord += [x]*3
        y_coord += list(range(2,-1,-1))
        timestamps += list(range(begin,end))
        begin += 1
        end += 1
    return x_coord, y_coord, timestamps

def get3x3CardinalPattern(begin_ts,mvmt):
    events = np.zeros((4,9))
    cardinal_mvmts = {
        "N" : mvmtN(),
        "NE": mvmtNE(),
        "E" : mvmtE(),
        "SE": mvmtSE(),
        "S" : mvmtS(),
        "SW": mvmtSW(),
        "W" : mvmtW(),
        "NW": mvmtNW()
    }
    events[::,0], events[::,1],events[::,3] = cardinal_mvmts[mvmt]
    events[::,3] += begin_ts
    
    return events, np.max(events[::,3])+1

def get2Dpattern(user, length_empty=None, nb_sequences=None):
    global description
    
    events = np.zeros((0,4))
    begin_ts = 0

    print("\nCardinal movements :\n-N: from south to north\n-NE: from south-west to north-east\n-E: from west to east\n-SE: from north-west to south-east\n-S: from north to south\n-SW: from north-east to south-west\n-W: from east to west\n-NW: from south-east to north-west")
    mvmt = input("Which cardinal movement ? ")
    
    if user == "F":
        nb_mvt = testNumericalInput(input("How many time the cardinal movement "+mvmt+" ? "))
        description += str(nb_mvt)+" repetitions of the same cardinal movement "+mvmt+";"
        full_pattern = np.zeros((0,4))
        pattern_begin_ts = begin_ts

        for _ in range(nb_mvt):
            pattern, pattern_begin_ts = getMorse1Dpattern(pattern_begin_ts, mvmt)
            full_pattern = np.concatenate((full_pattern, pattern), axis=0)

        for _ in range(nb_sequences):
            begin_ts=getEmptyPattern(begin_ts, length_empty)
            events = np.concatenate((events, np.concatenate((full_pattern[::,:3], full_pattern[::,3:]+begin_ts), axis=1) ), axis=0)
            begin_ts += pattern_begin_ts


def getPattern():
    global description
    user = size_sequence = size_empty = nb_sequences = None
    
    while user not in ["A","B","C","D","E","F","G","H"]:
        user = input("Which type of pattern ? (see patterns.csv) ")
    
    if user in ["A","B"]:
        size_sequence = testNumericalInput(input("Size of sequence ? "))
    if user in ["A", "B", "D", "E", "F"]: 
        size_empty = testNumericalInput(input("How long without events between the patterns/event sequences ? "))
        nb_sequences = testNumericalInput(input("How many event sequences ? "))
        description+=str(nb_sequences)+" sequences, separated by "+str(size_empty)+" timesteps;"
    
    if user in ["A","B","C","D","E"]:
        events = get1Dpattern(user,length_pattern=size_sequence, length_empty=size_empty, nb_sequences=nb_sequences)
    elif user in ["F","G","H"]:
        events = get2Dpattern(user,length_empty=size_empty, nb_sequences=nb_sequences)

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

# print(getPattern())