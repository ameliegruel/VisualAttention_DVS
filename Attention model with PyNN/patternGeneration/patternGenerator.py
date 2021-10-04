"""
Event-camera like patterns generator
Author : Amélie Gruel - Université Côte d'Azur, CNRS/i3S, France - amelie.gruel@i3s.unice.fr
"""

import numpy as np

def getPoisson1Dpattern(begin, length):
    return np.sort(np.random.poisson(begin+length/2, length))

def getConstant1Dpattern(begin,length):
    return np.arange(begin, begin+length)

def get1Dpattern(begin, length, user):
    events = np.zeros((length,4))
    events[::,2] = np.ones((length,))
    
    if user == "A":
        events[::,3] = getConstant1Dpattern(begin, length)
    elif user == "B":
        events[::,3] = getPoisson1Dpattern(begin,length)

    return events


def get2Dpattern(begin, length, nb_pixels):
    events = np.zeros((length,))


def getPattern():
    user=""
    while user not in ["A","B", "C", "D"]:
        user = input("Which type of pattern ? (see patterns.csv) ")
    events = get1Dpattern(250,250, user)

    filename=normalized_filename()
    np.save("")
    return events

print(getPattern())