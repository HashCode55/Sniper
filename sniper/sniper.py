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
from .errors import NotImplementedError, SniperError

# TODO Make an exec flag 
# TODO Make find realtime
# TODO Change editor functionality 
# TODO Tests 
# TODO name should include multiple words 
# TODO formatting of almost everythin 
# TODO Docs 
# TODO Server
# TODO database toggle 
# TODO ask for name adnd desc in prompt and else simply 

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
def run():
    """
    Executes the command stored with exec flag 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def push():
    """
    Shareing the note via gist. Requires login. 
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def fetch():
    """
    Push the note to gist. 
    Doesn't require login     
    """    
    raise NotImplementedError('Not implemented')

@sniper.command()
def shoot():
    """
    Code is incomplete without Easter Eggs
    """
    raise NotImplementedError('Not implemented')

