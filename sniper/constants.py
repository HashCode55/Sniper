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
# POST_SNIPPET   = 'https://sniper-manager.herokuapp.com/push'
# PULL_SNIPPET   = 'https://sniper-manager.herokuapp.com/pull' 
# SIGNIN         = 'https://sniper-manager.herokuapp.com/signin'
# SIGNUP		 = 'https://sniper-manager.herokuapp.com/signup'
# GET			 = 'https://sniper-manager.herokuapp.com/pull' 
POST_SNIPPET   = 'http://127.0.0.1:12345/push'
POSTALL        = 'http://127.0.0.1:12345/pushall'
PULLALL        = 'http://127.0.0.1:12345/pullall'
PULL_SNIPPET   = 'http://127.0.0.1:12345/pull' 
SIGNIN         = 'http://127.0.0.1:12345/signin'
SIGNUP		   = 'http://127.0.0.1:12345/signup'
GET			   = 'http://127.0.0.1:12345/pull' 

LJUST		   = 28