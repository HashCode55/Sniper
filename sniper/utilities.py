"""
Utilities for Sniper 

author: HashCode55
data  : 12/12/17
"""

import json 
from .constants import STORE

def open_store():
    """
    Opens the json file and returns the data as dict object 
    """
    with open(STORE) as d:
        data = json.load(d) 
    return data           

def save_store(data):    
    """
    Saves the dict object in store 

    params@data: The dict object to be stored 
    """
    with open(STORE, 'w+') as d:
        json.dump(data, d) 
