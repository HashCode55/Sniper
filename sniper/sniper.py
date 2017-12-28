"""
The Engine. Sniper lives here.

author: HashCode55
data  : 09/12/2017
"""

import click
import pickle
import json
import os 
import clipboard

from fuzzywuzzy import process

from .utilities import open_store, save_store
from .parser import Parser
from .errors import NotImplementedError, SniperError, ServerError
from .constants import POST_SNIPPET, TOKEN_FILE, SIGNUP, SIGNIN, PULL_SNIPPET

from urllib.parse import urlencode
from urllib.request import Request, urlopen


#### PRIORITY LEVEL - HIGH ####
# TODO remove parser 
# TODO Make an exec flag 
# TODO Tests 
# TODO Docs 
# TODO Server

#### PRIORITY LEVEL - LOW ####
# TODO formatting of almost everythin 
# TODO client database toggle 
# TODO Make find realtime
# TODO Change editor functionality 
# TODO name should include multiple words 

@click.group()
def sniper():
    """
    Sniper is a simple snippet manager which increases your productivity
    by saving your most used snippets and giving an easy interface to extract them as well
    """
    pass

@sniper.command()
@click.option('-q', is_flag = True)
def new(q):
    """
    Name of the file you want to create
    """
    data = {}
    if q == True:
        name = click.prompt('NAME')   
        name = name.strip()     
        if name == '':
            raise SniperError('NAME cannot be empty')
        desc = click.prompt('DESC')             
        command = click.prompt('COMMAND')
        name = name.strip()
        desc = desc.strip()
        code = command.strip()
        data = {
            name: {
                'DESC': desc, 'CODE': command                    
            } 
        }
    else:    
        # prompt the user to create a snippet 
        snipe = click.edit('NAME :\nDESC :\nCODE :')
        # parse the input to check for any errors 
        parser = Parser(snipe)
        parser.validate_input()
        # get the map        
        data = parser.create_map()                
    
    # open the default store 
    load = open_store()    
    # update the store     
    load.update(data)    
    # store the data 
    save_store(load)
    
@sniper.command()        
@click.argument('snippet')
def get(snippet):
    """
    Use get to extract the snipper 
    Copies to the clipboard 

    params@snippet: Snippet name 
    """
    # open the json file 
    data = open_store()
    # check if the given name exists 
    if not snippet in data.keys():
        raise SniperError('No snipped exists with the name: ' + snippet)         
    try:    
        clipboard.copy(data[snippet]['CODE'])
    except SniperError:
        raise SniperError('Failed to copy to clipboard.')
    click.echo('Code successfully copied to clipboard.')    


@sniper.command()
@click.argument('snippet')
def rm(snippet):
    """
    Remove a snippet from the store 

    params@snippet: Snippet name 
    """    
    # open the json file 
    data = open_store()
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snipped exists with the name: ' + snippet)         
    else:
        data.pop(snippet)                       
    # save the new dict     
    save_store(data)
    click.echo('Snippet successfully deleted.')    

@sniper.command()
def ls():
    """
    List the snippets pretty printing the name and desc of the 
    stored snippets  
    """    
    # load the data 
    data = open_store()
    if len(data) == 0:
        click.echo('No snippets stored. Use "snippet new" to create a new snippet')
        return 
    # TODO check for errors here     
    name_h, desc_h = 'NAME', 'DESC'
    click.echo(name_h.ljust(30) + desc_h.ljust(30))    
    click.echo('-'*60)  
    for name, dat in data.items():
        name = name.ljust(30)
        dat = dat['DESC'].ljust(30)
        click.echo(name + dat)                

@sniper.command()
@click.argument('snippet')
def cat(snippet):
    """
    Displaying the command 
    """
    data = open_store()        
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snipped exists with the name: ' + snippet)         
    else:
        click.echo(data[snippet]['CODE'])

@sniper.command()
@click.argument('snippet')
def edit(snippet):
    """
    For editing the snippet 
    """    
    # get the data 
    data = open_store()        
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snipped exists with the name: ' + snippet)         
    # take the input parse it again and save a new file    
    edit = 'NAME : {}\nDESC : {}\nCODE : {}'.format(snippet, data[snippet]['DESC'], data[snippet]['CODE'])
    snipe = click.edit(edit)    
    # parse, check and create     
    parser = Parser(snipe)
    # validate the input 
    parser.validate_input()
    # get the map
    new_data = parser.create_map()        
    # update the original dic 
    data.update(new_data)
    # store the new data back 
    save_store(data)
    click.echo('Snippet successfully edited.')    


@sniper.command()
@click.argument('query')
def find(query):
    """
    Find the snippet
    """                                       
    # give preference to the name first 
    data = open_store()
    names = list(data.keys())
    # get the result 
    result = process.extract(query, names)
    # now do the same based on description 
    descriptions = {nest['DESC']:name for name, nest in data.items()}
    # update the result 
    result.extend(process.extract(query, list(descriptions.keys())))        
    result.sort(key = lambda x: x[1], reverse=True)
    # now simply print the first 5 results 
    click.echo("These are the top five matching results: \n\n")
    name_h, desc_h = 'NAME', 'DESC'
    click.echo(name_h.ljust(30) + desc_h.ljust(30))    
    click.echo('-'*60)     
    
    result = list(set(result))     
    result = result[:5]
    for res, _ in result:        
        if res in data.keys():
            name = res 
            dat = data[name]['DESC']
        else:
            name = descriptions[res]
            dat = res
        name = name.ljust(30)
        dat = dat.ljust(30)    
        click.echo(name + dat)    

@sniper.command()
def reset():
    """
    Removes all the snippets 
    """
    click.confirm('Are you sure you want to remove all the snippets?')
    save_store({})
    click.echo('Successfully deleted.')

@sniper.command()
@click.argument('snippet')
@click.option('-p', is_flag = True)
def push(snippet, p):
    """
    Sharing the note via gist. Requires login. 
    """        
    # get the data 
    data = open_store()                
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)
    
    # check whether the user has logged in or not 
    with open(TOKEN_FILE) as t:
        token = t.read()        
    if token == '':        
        authenticate()                        

    # read again updated     
    with open(TOKEN_FILE) as t:
        token = t.read()            
    token = token.split('\n')
    if len(token) < 2:
        raise SniperError('Credentials File is Corrupt. Please report this issue on Github.')
    username = token[1]
    token = token[0]     
    
    # by default the snippet is public 
    private = False
    if p: private = True  
    
    # cook the json 
    jdata = {    
        'user': username,        
        'priv': private,
        'name': snippet, 
        'desc': data[snippet]['DESC'],
        'code': data[snippet]['CODE'], 
        'token': token
    }    
    res = post(jdata, POST_SNIPPET)   
    click.echo('Saved on server.') 
    
@sniper.command()
@click.argument('snippet')
@click.option('-user', default='', type=str)
def pull(snippet, user):
    """
    pull the public snippet 
    and save it locally 
    """    
    # check if the user is specified 
    if user != '':
        # simply get the data 
        req = {
            'user': user, 
            'name': snippet,
            'token': '',             
        }
        res = post(req, PULL_SNIPPET)
    else:            
        # username is specified 
        with open(TOKEN_FILE) as t:
            token = t.read()        
        if token == '':        
            authenticate()       
        # open again to read data after authentication     
        with open(TOKEN_FILE) as t:
            token = t.read()                
        token = token.split('\n')
        if len(token) < 2:
            raise SniperError('Credentials File is Corrupt. Please report this issue on Github.')
        username = token[1]
        token = token[0]                
        # cook the send the request 
        req = {
            'user': username,
            'name': snippet, 
            'token': token
        }        
        res = post(req, PULL_SNIPPET)

    # get the data 
    data = open_store()                
    # save the snippet locally     
    new_data = {
        res['data']['name']: {
            'DESC': res['data']['desc'], 
            'CODE': res['data']['code']
        }
    }
    data.update(new_data)    
    save_store(data)
    click.echo('Snippet Successfully Saved.')

@sniper.command()
def signout():
    """
    Signout from sniper 
    """
    with open(TOKEN_FILE, 'w') as t:
        t.write('')
    click.echo('Successfully signed out.')    

@sniper.command()
def run():
    """
    Executes the command stored with exec flag 
    """    
    raise NotImplementedError('Not implemented')
    

@sniper.command()
def shoot():
    """
    Code is incomplete without Easter Eggs
    """
    raise NotImplementedError('Not implemented')

####################
# HELPER FUNCTIONS #
####################

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
    

