"""
This is the main file which creates a default config
and fires up sniper commands

author: hashcode55
date  : 09/12/2017
"""

import os 
import json
from .sniper import sniper
from .constants import variables

def run (): 
    """
    Create a config file or ignore if it's 
    """            
    # check if there is a directory         
    if not os.path.exists(variables['PATH']):
        print ('made a directort')
        os.makedirs(variables['PATH'])                    
    # check the data file 
    if not os.path.isfile(variables['PATH'] + '/' + 'data.json'):
        file = open(variables['PATH'] + '/' + 'data.json', 'a')
        file.close()
        with open(variables['PATH'] + 'data.json', 'w+') as d:
            json.dump({}, d)    
    # TODO    
    # check if config file exists 
    # if not create one else read it and change setting 

    # call sniper main command 
    sniper()            