#!/usr/bin/python3

import pickle
from datetime import datetime

debug = False

def bug(s,newline=True):
    "Like print but only if the environment variable called debug is true."
    if debug:
        if newline:
            print(s)
        else:
            print(s,end="")

def weed(dates):
    newdates = []
    for date in dates:
        if date < datetime.now() and date != datetime(2014, 9, 19, 0, 0):
            newdates.append(date)
        else:
            print("Dropped.")
    return newdates

def hsps_pickle(dates):
    pickle.dump(dates,open('dates2.pic','wb'))
    print('New file: dates2.pic')

def hsps_unpickle():
    "Returns dates."
    dates = pickle.load(open('dates.pic','rb'))
    print(dates)
    bug('Unpickled...')
    return dates

hsps_pickle(weed(hsps_unpickle()))

