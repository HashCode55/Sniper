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
from .utilities import open_store, save_store, get_token_username, post, authenticate
from .errors import NotImplementedError, SniperError, ServerError
from .constants import POST_SNIPPET, PULL_SNIPPET, SIGNUP, SIGNIN, TOKEN_FILE, LJUST, POSTALL, PULLALL

@click.group()
def sniper():
    """
    Sniper is a clould enabled, terminal based easy to use snippet manager.To begin, try saving a snippet/command 
    using the "new" command.

    - sniper new
    """
    pass

@sniper.command()
@click.option('-e', default=False, is_flag=True, help='Provide this flag if the snippet is executable')
@click.option('-t', default=False, is_flag=True)
def new(e, t):
    """
    For creating a new snippet.

    USAGE

    - sniper new 
    """
    # open the default store 
    data = open_store()        
    name = click.prompt('NAME')       
    if name == '':
        raise SniperError('NAME cannot be empty')    
    name = name.strip().lower()    
    if name in data.keys():
        raise SniperError('Snippet with this name already exists.')
    desc = click.prompt('DESC')                     
    desc = desc.strip()
    # take the input through the editor 
    code = click.edit('') if not t else click.prompt('CODE')    
    code = code.strip()  
    # cook the data to be saved                 
    curtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data = {
        name: {
            'DESC': desc, 
            'CODE': code, 
            'EXEC': e, 
            'TIME': curtime                 
        } 
    }    
    # update the store     
    data.update(new_data)    
    # store the data 
    save_store(data)
    click.echo('Snippet successfully saved.')
    
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
    snippet = snippet.strip().lower()
    # check if the given name exists 
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)         
    try:    
        clipboard.copy(data[snippet]['CODE'])
    except:
        raise SniperError('Failed to copy to clipboard.')
    click.echo('Snippet successfully copied to clipboard.')    

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
    snippet = snippet.strip().lower()
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)         
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
    snippet = snippet.strip().lower()      
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
    snippet = snippet.strip().lower()      
    # check if the snippet exists in keys 
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)         
    
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
    query = query.strip().lower()
    names = list(data.keys())
    if len(names) == 0: 
        raise SniperError('No snippets saved.')        
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
    Executes the command if stored with "-e" (executable) flag.

    USAGE 
    
    - sniper run <snippet-name>
    """        
    data = open_store()   
    snippet = snippet.strip().lower()             
    if not snippet in data.keys():
        raise SniperError('No snippet exists with the name: ' + snippet)
    if not data[snippet]['EXEC']:
        raise SniperError('Snippet not executable.')
    if os.name == 'nt':
        exitcode = subprocess.call(data[snippet]['CODE'].split(' '), shell=True)        
    else:
        exitcode = subprocess.call(data[snippet]['CODE'].split(' '))    
    if exitcode != 0: 
        raise SniperError('Error running the snippet.')

@sniper.command()
def clear():
    """
    Removes all the snippets. 

    USAGE

    - sniper reset 
    """
    res = click.confirm('Are you sure you want to remove all the snippets locally?')
    if res:
        save_store({})
        click.echo('Successfully reset.')

@sniper.command()
@click.option('-s', help='Name of specific snippet to be pushed.')
@click.option('-p', is_flag = True, help='To store the specific snippet as private.')
def push(s, p):
    """
    Store all the snippets or a single snippet on cloud.

    USAGE

    - sniper push 

    - sniper push -s=<snippet-name>
    """        
    # get the data 
    data = open_store()                
    if len(data) == 0: 
        raise SniperError('No snippets to push.')

    # get token and username 
    token, username = get_token_username(True)     
    
    # by default it'll push all the snippets 
    if s == None:
        # modify data to store name as 'NAME'
        temp_data = [{'NAME':d} for d in data.keys()]
        for td in temp_data:
            td.update(data[td['NAME']])
        jdata = {
            'user': username,
            'data': temp_data,
            'token': token
        }
        res = post(jdata, POSTALL)
        if 'info' in res.keys():
            click.echo(res['info'])
        elif 'err' in res.keys() and res['err'] != '':
            raise ServerError(res['err'])    
        # finish
        return 

    # logic for specific snippet 
    s = s.strip().lower()
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
@click.option('-s', type=str, help='Specific snippet to be retrieved.')
@click.option('-user', type=str, help='For getting other users public snippets.')
def pull(s, user):
    """
    Get all the snippets or a single snippet from cloud.

    USAGE

    - sniper pull <snippet-name>
    """    
    data = open_store()
    # -user flag cannot be used alone 
    if s == None and user != None: 
        raise SniperError('Cannot pull all snippets of a different user.')
    # pullall is used     
    if s == None:     
        token, username = get_token_username(False)
        req = {
            'user': username,
            'token': token                
        }
        # response would be array of snippets 
        res = post(req, PULLALL)
        if 'err' in res.keys() and res['err'] != '':
            raise ServerError(res['err'])
        if res['data'] == None:
            raise ServerError('No snippets saved on server.')    
        for snippet in res['data']:
            # check if already exists 
            if snippet['name'] in data.keys():
                # compare the time 
                serversnip_time = datetime.strptime(snippet['time'], '%Y-%m-%d %H:%M:%S')    
                localsnip_time = datetime.strptime(data[snippet['name']]['TIME'], '%Y-%m-%d %H:%M:%S')    
                # ignore if equal or less 
                if serversnip_time <= localsnip_time: continue                     
            # else update the data 
            new_data = {
                snippet['name']: {
                    'DESC': snippet['desc'], 
                    'CODE': snippet['code'],
                    'EXEC': snippet['exec'],
                    'TIME': snippet['time']
                }                        
            }
            data.update(new_data)    
    else:        
        s = s.strip().lower()
        # snippet is specified            
        # check if the user is specified 
        if user != None:
            # check if specified username is same as logged in user 
            with open(TOKEN_FILE) as t:
                token = t.read()
            req_set = False   
            if token != '':
                token = token.split('\n')
                if len(token) < 2:
                    raise SniperError('Credentials File is Corrupt. Please report this issue on Github.')
                username = token[1]
                token = token[0]
                if username == user:                    
                    req = {
                        'user': username,
                        'name': s, 
                        'token': token
                    }  
                    req_set = True      
            # simply get the data 
            if not req_set:
                req = {
                    'user': user, 
                    'name': s,
                    'token': '',             
                }
            res = post(req, PULL_SNIPPET)
        # just snippet is specified     
        else:            
            token, username = get_token_username(False)
            # cook the send the request 
            req = {
                'user': username,
                'name': s, 
                'token': token
            }        
            res = post(req, PULL_SNIPPET)
        # check for errors 
        if 'err' in res.keys() and res['err'] != '':
            raise ServerError(res['err'])        
        if len(res['data']) == 0:
            raise ServerError('Error pulling from server. No snippets pulled.')
        # save the snippet locally     
        snippet = res['data'][0]
        new_data = {
            snippet['name']: {
                'DESC': snippet['desc'], 
                'CODE': snippet['code'],
                'EXEC': snippet['exec'],
                'TIME': snippet['time']
            }
        }
        data.update(new_data)    
    # save the data finally     
    save_store(data)
    click.echo('Successfully pulled from server.')

@sniper.command()
def logout():
    """
    Logout from sniper. 

    USAGE 

    - sniper logout
    """    
    try:        
        with open(TOKEN_FILE, 'w') as t:
            t.write('')
    except:
        raise SniperError('Error opening the credentials file.')            
    click.echo('Successfully signed out.')    

@sniper.command()
def login():
    """
    Login to sniper 

    USAGE 

    - sniper login
    """    
    authenticate(True)

@sniper.command()
def whoami():
    """
    Displays the username.

    USAGE 

    - sniper whoami
    """
    try:
        with open(TOKEN_FILE) as t:
            token = t.read()        
    except:
        raise SniperError('Error reading the credentials file.')            
    if token == '':
        raise SniperError('You are currently not logged in.')
    token = token.split('\n')
    if len(token) < 2:
        raise SniperError('Credentials file is corrupt. Please report this issue on Github.')
    click.echo(token[1])    

####           IMPLEMENT THIS LATER            ####
#### CURRENTLY COMMENTED OUT TO NOT SPOIL DOCS ####

# @sniper.command()
# def shoot():
#     """
#     Shoot a bullet.
#     """
#     raise NotImplementedError('Not implemented')
