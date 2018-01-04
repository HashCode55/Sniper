"""
The Engine. Sniper lives here.

author: HashCode55
data  : 09/12/2017
"""

import click
import json
import os 
import clipboard
import subprocess

from fuzzywuzzy import process

from datetime import datetime
from .utilities import open_store, save_store, authenticate, post 
from .errors import NotImplementedError, SniperError, ServerError
from .constants import POST_SNIPPET, PULL_SNIPPET, SIGNUP, SIGNIN, TOKEN_FILE, LJUST, POSTALL

#### PRIORITY LEVEL - HIGH ####
# TODO[DONE] remove parser, name desc and command in editore  
# TODO[DONE] ls formatting 
# TODO[DONE] Edit formatting  
# TODO[DONE] Find 
# TODO[DONE] Make an exec flag 
# TODO[DONE] Tests 
# TODO[DONE] Docs 
# TODO[DONE] Final refactoring
# TODO[DONE] Store time and update server  
# TODO push all pull all 
# TODO Test on multiple platforms 
# TODO Final refactoring

#### PRIORITY LEVEL - LOW ####
# TODO storage structure change
# TODO Make find realtime

@click.group()
def sniper():
    """
    Sniper is a simple snippet manager. To begin, try saving a snippet/command using the 
    "new" command.

    - sniper new
    """
    pass

@sniper.command()
@click.option('-e', default=False, is_flag=True, help='Provide this flag if the command/snippet is executable')
@click.option('-t', default=False, is_flag=True)
def new(e, t):
    """
    For creating a new snippet.

    USAGE

    - sniper new 
    """
    data = {}    
    name = click.prompt('NAME')       
    if name == '':
        raise SniperError('NAME cannot be empty')
    desc = click.prompt('DESC')                 
    name = name.strip()
    desc = desc.strip()
    # take the input through the editor 
    code = click.edit('') if not t else click.prompt('CODE')    
    code = code.strip()  
    # cook the data to be saved                 
    curtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        name: {
            'DESC': desc, 
            'CODE': code, 
            'EXEC': e, 
            'TIME': curtime                 
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
    For copying the snippet to the clipboard.

    USAGE 

    - sniper get <snippet-name>    
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
    Remove a snippet locally. 

    USAGE

    - sniper rm <snippet-name>    
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
    List the snippets. 

    USAGE

    - sniper ls 
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
    Display the code.

    Usage

    - sniper cat <snippet-name>
    """
    data = open_store()        
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)         
    else:
        click.echo(data[snippet]['CODE'])

@sniper.command()
@click.argument('snippet')
@click.option('-t', default=False, is_flag=True, help='For testing.')
def edit(snippet, t):
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
    new_code = click.edit(data[snippet]['CODE']) if not t else click.prompt('CODE')   
    new_code = new_code.strip()
    # update the time 
    new_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            'EXEC': new_exec,
            'TIME': new_time
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
    For finding a snippet. Shows the top five matches.
    
    USAGE 

    - sniper find <query>
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
    Executes the command if stored with "-e" flag.

    USAGE 
    
    - sniper run <snippet-name>
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
    Removes all the snippets. 

    USAGE

    - sniper reset 
    """
    res = click.confirm('Are you sure you want to remove all the snippets?')
    if res:
        save_store({})
        click.echo('Successfully reset.')

@sniper.command()
@click.option('-s', help='Specific snippet to be pushed.')
@click.option('-p', is_flag = True, help='To store the snippet as a private.')
def push(s, p):
    """
    Push all the snippets to cloud or just push a single snippet. 
    Use "sniper push --help" for more info.

    USAGE

    - sniper push 
    - sniper push -s=<snippet-name>
    """        
    # get the data 
    data = open_store()                

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
    
    # by default it'll push all the snippets 
    if s == None:
        jdata = {
            'user': username,
            'data': data,
            'token': token
        }
        post(jdata, POSTALL)
        # finish
        return 

    # logic for specific snippet    
    if not s in data.keys():
        raise SniperError('No snippet exists with the name: ' + s)

    # by default the snippet is public 
    private = False
    if p: private = True  
    
    # cook the json 
    jdata = {    
        'user': username,        
        'priv': private,
        'name': s, 
        'desc': data[s]['DESC'],
        'code': data[s]['CODE'], 
        'token': token,
        'exec': data[s]['EXEC'],
        'time': data[s]['TIME']
    }    
    res = post(jdata, POST_SNIPPET)   
    if 'info' in res.keys():
        click.echo(res['info'])
    else:
        click.echo('Saved on server.') 
    
@sniper.command()
@click.argument('snippet')
@click.option('-user', default='', type=str, help='For getting other users\' public snippets.')
def pull(snippet, user):
    """
    Get the snippet from the cloud. Use "sniper pull --help" for 
    more info.

    USAGE

    - sniper pull <snippet-name>
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
            'CODE': res['data']['code'],
            'EXEC': res['data']['exec'],
            'TIME': res['data']['time']
        }
    }
    data.update(new_data)    
    save_store(data)
    click.echo('Snippet Successfully Saved.')

@sniper.command()
def logout():
    """
    Logout from sniper. 

    USAGE 

    - sniper logout
    """
    with open(TOKEN_FILE, 'w') as t:
        t.write('')
    click.echo('Successfully signed out.')    

@sniper.command()
def whoami():
    """
    Displays the username.

    USAGE 

    - sniper whoami
    """
    with open(TOKEN_FILE) as t:
            token = t.read()                
    if token == '':
        raise SniperError('You are currently not logged in.')
    token = token.split('\n')
    if len(token) < 2:
        raise SniperError('Credentials File is Corrupt. Please report this issue on Github.')
    click.echo(token[1])    

####           IMPLEMENT THIS LATER            ####
#### CURRENTLY COMMENTED OUT TO NOT SPOIL DOCS ####

# @sniper.command()
# def shoot():
#     """
#     Shoot a bullet.
#     """
#     raise NotImplementedError('Not implemented')
