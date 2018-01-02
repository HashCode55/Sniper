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
TOKEN_FILE     = PATH + '.token'
POST_SNIPPET   = 'http://192.168.1.40:12345/push'
PULL_SNIPPET   = 'http://192.168.1.40:12345/pull' 
SIGNIN         = 'http://192.168.1.40:12345/signin'
SIGNUP		   = 'http://192.168.1.40:12345/signup'
GET			   = 'http://192.168.1.40:12345/pull' 
LJUST		   = 28