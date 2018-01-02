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
import subprocess

from fuzzywuzzy import process

from .utilities import open_store, save_store, authenticate, post 
from .parser import Parser
from .errors import NotImplementedError, SniperError, ServerError
from .constants import POST_SNIPPET, TOKEN_FILE, SIGNUP, SIGNIN, PULL_SNIPPET, LJUST

from urllib.parse import urlencode
from urllib.request import Request, urlopen


#### PRIORITY LEVEL - HIGH ####
# TODO[DONE] remove parser, name desc and command in editore  
# TODO[DONE] ls formatting 
# TODO[DONE] Edit formatting  
# TODO[DONE] Find 
# TODO pushh all pull all 
# TODO[DONE] Make an exec flag 
# TODO Tests 
# TODO Docs 
# TODO Final refactoring 

#### PRIORITY LEVEL - LOW ####
# TODO storage structure change
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
@click.option('-e', default=False)
def new(e):
    """
    Name of the file you want to create
    includes the exec flag if the command to save can be executed 
    """
    data = {}    
    name = click.prompt('NAME')       
    if name == '':
        raise SniperError('NAME cannot be empty')
    desc = click.prompt('DESC')                 
    name = name.strip()
    desc = desc.strip()
    # take the input through the editor 
    code = click.edit('')  
    code.strip()  
    # cook the data to be saved                 
    data = {
        name: {
            'DESC': desc, 'CODE': code, 'EXEC': e                 
        } 
    }
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
    click.echo('Total: ' + str(len(data)))  
    name_h, desc_h = 'NAME', 'DESC'
    click.echo(name_h.ljust(LJUST) + desc_h.ljust(LJUST))    
    click.echo('-'*LJUST*2)  
    for name, content in data.items():
        # name of snippet 
        name = name.ljust(LJUST)
        desc = content['DESC']
        # format the description     
        if len(desc) > 25: 
            desc = desc[:25] + '...'
        dat = desc.ljust(LJUST)
        click.echo(name + desc)                

@sniper.command()
@click.argument('snippet')
def cat(snippet):
    """
    Displaying the command 
    """
    data = open_store()        
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)         
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
    new_name = click.prompt('NAME', default=snippet)
    new_desc = click.prompt('DESC', default=data[snippet]['DESC'])
    new_exec = click.prompt('EXEC', default=data[snippet]['EXEC'], type=bool)    
    new_code = click.edit(data[snippet]['CODE'])    
    new_code = new_code.strip()
    if new_name == '':
        new_name = snippet
    if new_desc == '':
        new_desc = data[snippet]['DESC']
    if new_exec == None:
        new_exec = data[snippet]['EXEC']    
    new_data = {
        new_name: {
            'DESC': new_desc,
            'CODE': new_code,
            'EXEC': new_exec
        }
    }
    data.pop(snippet)
    # remove the old snippet 
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
    # merge key name and description just for searching 
    # putting it in dit for extraction 
    content = {(key + ' ' + data[key]['DESC']):key for key in data.keys()}
    # get the result 
    result = process.extract(query, content.keys())    
    # extract
    result = [(content[data], score) for data, score in result]        
    # now simply print the first 5 results 
    click.echo("These are the top five matching results: \n")
    name_h, desc_h = 'NAME', 'DESC'
    click.echo(name_h.ljust(LJUST) + desc_h.ljust(LJUST))    
    click.echo('-'*LJUST*2)     
    # use set to remove duplicate entries     
    result = list(set(result))     
    result.sort(key = lambda x: x[1], reverse=True)
    result = result[:5]
    # print the result     
    for name, _ in result:                        
        desc = data[name]['DESC']        
        name = name.ljust(LJUST)
        if len(desc) > 25:
            desc = desc[:25] + '...'
        desc = desc.ljust(LJUST)    
        click.echo(name + desc)    

@sniper.command()
@click.argument('snippet')
def run(snippet):
    """
    Executes the command stored with exec flag 

    """        
    data = open_store()                
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)
    if not data[snippet]['EXEC']:
        raise SniperError('Snippet not executable.')
    exitcode = subprocess.call(data[snippet]['CODE'].split(' '))    
    if exitcode != 0: 
        raise SniperError('Error running the snippet.')

@sniper.command()
def reset():
    """
    Removes all the snippets 
    """
    res = click.confirm('Are you sure you want to remove all the snippets?')
    if res:
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
    if 'info' in res.keys():
        click.echo(res['info'])
    else:
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
def logout():
    """
    Signout from sniper 
    """
    with open(TOKEN_FILE, 'w') as t:
        t.write('')
    click.echo('Successfully signed out.')    


@sniper.command()
def shoot():
    """
    Code is incomplete without Easter Eggs
    """
    raise NotImplementedError('Not implemented')
