"""
The Engine. Sniper lives here.

author: HashCode55
data  : 09/12/2017
"""

import click
import pickle
import json
import os 

from .constants import variables 
from .helper import Parser
from .errors import NotImplementedError, SniperError

@click.group()
def sniper():
    """
    Sniper is a simple snippet manager which increases your productivity
    by saving your most used snippets and giving an easy interface to extract them as well

    - Create a new snippet\n
        sniper new snippet
    - Extract a snippet\n 
        snipet get snippet
    - Remove a snippet 
        sniper rm snippet 
    - List snippets 
        sniper ls              
    """
    pass

@sniper.command()
@click.option('-q', type=bool, default=False)
def new(q):
    """
    Name of the file you want to create
    """
    data = {}
    if q == True:
        name = click.prompt('NAME')        
        if name.strip() == '':
            raise SniperError('NAME cannot be empty')
        desc = click.prompt('DESC')             
        command = click.prompt('COMMAND')
        data = {
            name: {
                'DESC': desc, 'CODE': command                    
            } 
        }
    else:    
        # prompt the user to create a snippet 
        snipe = click.edit('NAME:\nDESC:\nCODE:')
        # parse the input to check for any errors 
        parser = Parser(snipe)
        parser.validate_input()
        # get the map
        data = parser.create_map()        
    
    # open the default store 
    with open(variables['PATH'] + 'data.json') as d:
        load = json.load(d)
    # update the store     
    load.update(data)    
    # store the data 
    with open(variables['PATH'] + 'data.json', 'w+') as d:
        json.dump(load, d)

    
@sniper.command()        
# @click.argument('snippet')
def get():
    """
    Use get to extract the snipper 
    Copies to the clipboard 
    """
    raise NotImplementedError('Not implemented')

@sniper.command()
def find():
    """
    Find the snippet
    """
    raise NotImplementedError('Not implemented')

@sniper.command()
def rm():
    """
    Remove a snippet 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def ls():
    """
    List the snippets 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def edit():
    """
    For editing the snippet 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def cat():
    """
    Displaying the command 
    """
    raise NotImplementedError('Not implemented')

@sniper.command()
def share():
    """
    Shareing the note via gist
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def push():
    """
    Push the note to gist 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def shoot():
    """
    Code is incomplete without Easter Eggs
    """
    raise NotImplementedError('Not implemented')




