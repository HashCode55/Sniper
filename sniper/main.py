"""
This is the main file which creates a default config
and fires up sniper commands

author: hashcode55
date  : 09/12/2017
"""

import os 
import json
from .sniper import sniper
from .constants import PATH, STORE, TOKEN_FILE

def run (): 
    """
    Create a config file or ignore if it's 
    """                
    # check if there is a directory         
    if not os.path.exists(PATH):
        print ('made a directory')
        os.makedirs(PATH)                    
    # check the data file 
    if not os.path.isfile(STORE):
        file = open(STORE, 'a')
        file.close()
        with open(STORE, 'w+') as d:
            json.dump({}, d) 
    # create a hidden file to store token         
    if not os.path.isfile(TOKEN_FILE):
        file = open(TOKEN_FILE, 'a')
        file.close()
    # TODO    
    # check if config file exists 
    # if not create one else read it and change setting 

    # call sniper main command 
    sniper()            