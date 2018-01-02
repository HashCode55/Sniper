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


def authenticate():
    """
    authenticate  
    """
    reg = click.confirm('Dang! You are not an authorized sniper :( Do you already have' + 
            ' an account?')
    if not reg:
        # get the username and password 
        yes = click.confirm('Well! Why not create one? Press y to confirm.')
        # fuck you, user 
        if not yes: exit(1) 
        username = click.prompt('Username', type=str)                        
        password = click.prompt('Password', type=str, hide_input=True, confirmation_prompt=True)
        # sweet password check 
        if len(password) < 8:
            while len(password) < 8:
                click.echo('Password must be atleast of 8 characters.')
                password = click.prompt('Password', type=str, hide_input=True, confirmation_prompt=True)
        res = post({'user': username, 'pass': password}, SIGNUP)                        
    else: 
        username = click.prompt('Username', type=str)
        password = click.prompt('Password', type=str, hide_input=True)
        res = post({'user': username, 'pass': password}, SIGNIN)
    
    if 'token' in res.keys() and res['token'] != '':
        # store the token 
        token = res['token']
        with open(TOKEN_FILE, 'w+') as t:
            t.write(res['token'] + '\n' + username)
        click.echo('Signed in.')                
    else: 
        raise ServerError('Error signing in.')       

def post(data, url):
    """
    Client Post Request  
    """  
    data = json.dumps(data).encode('utf8')
    try: 
        request = Request(url, data=data)                   
        request.add_header('Content-Type', 'application/json')
        response = urlopen(request).read().decode('utf-8')
        # parse the string             
        response = json.loads(response)
    except ServerError: 
        raise ServerError('Couldn\'t connect to server.') 
    # check the server response     
    if not response['success']:             
        raise ServerError(response['err'])  
    return response        
    

