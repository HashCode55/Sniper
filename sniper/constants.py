"""
Contains the constants duh.

author: hashcode55
date  : 09/12/2017
"""

import os 

HOME  		   = os.environ['HOME']
DIRECTORY_NAME = '.sniper'
PATH  		   = HOME + '/' + DIRECTORY_NAME + '/'
STORE 		   = PATH + 'data.json'
POST 		   = 'http://192.168.1.40:12345/push' 
GET			   = 'http://192.168.1.40:12345/pull' 