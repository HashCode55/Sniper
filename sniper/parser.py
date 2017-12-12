"""
Contains the helpers of Sniper :)

author: HashCode55 
date  : 09/12/2017
"""

import re 

from .errors import ParserError

class Parser(object):
    """
    For snippet validation 
    """
    def __init__(self, snippet):
        """
        Constructor 
        """
        self.snippet = snippet
        # indices for for the sections of file
        # NAME SECTION
        self.name_sindex = -1
        self.name_eindex = -1
        # DESCRIPTION SECTION
        self.desc_sindex = -1
        self.desc_eindex = -1
        # CODE SECTION
        self.code_sindex = -1
        self.code_eindex = -1

    def validate_input(self):
        """
        Validates the input of the "new" command.

        params@snippet: snippet as input         
        """
        # trim for blank lines in the starting and ending of file 
        self.snippet = self.snippet.strip()
        # break the snippet of basis of '\n'
        snippet_split = self.snippet.split('\n')        
        num_of_lines = len(snippet_split)
        
        # check if first line is NAME 
        if not snippet_split[0].startswith('NAME'): 
            raise ParserError('Error Parsing the input. NAME field not present\n')
        # set the name indices    
        self.name_sindex = 0
        self.name_eindex = 0

        # check for the DESC field    
        index = 1
        while (index < num_of_lines):
            line = snippet_split[index].strip()
            # if it contains DESC field 
            if (line.startswith('DESC')): 
                break 
            index += 1 
        if index == num_of_lines:
            raise ParserError('Error Parsing the input. DESC field not present\n')        
        # set the desc start index     
        self.desc_sindex = index

        # find the CODE field 
        index += 1
        while (index < num_of_lines):
            line = snippet_split[index].strip()
            # if it contains DESC field 
            if (line.startswith('CODE')): 
                self.desc_eindex = index - 1
                break 
        if index == num_of_lines:
            raise ParserError('Error Parsing the input. CODE field not present\n')        
        # set the code section start index 
        self.code_sindex = index 
        self.code_eindex = num_of_lines - 1    

    def create_map(self):
        """
        Creates a dict to be stored in json file from the input of 
        "new" command 

        params&snippet: validated snippet 
        returns&dict  : The validated map created
        """        
        snippet_split = self.snippet.split('\n')        
        
        # NAME FIELD 
        # find and remove 'NAME' and ':' to get the name 
        name_sind = self.name_sindex
        snippet_split[name_sind] = snippet_split[name_sind].lstrip('NAME')
        # remove any space         
        snippet_split[name_sind] = snippet_split[name_sind].lstrip()
        # remove the ':' if exists 
        if snippet_split[name_sind].startswith(':'):
            snippet_split[name_sind] = snippet_split[name_sind].lstrip(':')
        else:
            raise ParserError('Bad Syntax. ":" missing in NAME field.')
        name = '\n'.join(snippet_split[name_sind:self.name_eindex+1])
        name = name.strip()
        # check if it is empty 
        if name == '':
            raise ParserError('NAME fielf cannot be empty')

        # DESC FIELD
        desc_sind = self.desc_sindex
        snippet_split[desc_sind] = snippet_split[desc_sind].lstrip('DESC')
        # remove any space         
        snippet_split[desc_sind] = snippet_split[desc_sind].lstrip()
        # remove the ':' if exists 
        if snippet_split[desc_sind].startswith(':'):
            snippet_split[desc_sind] = snippet_split[desc_sind].lstrip(':')
        else:
            raise ParserError('Bad Syntax. ":" missing in DESC field.')
        desc = '\n'.join(snippet_split[desc_sind:self.desc_eindex+1])

        # get the code field 
        code_sind = self.code_sindex
        snippet_split[code_sind] = snippet_split[code_sind].lstrip('CODE')
        # remove any space         
        snippet_split[code_sind] = snippet_split[code_sind].lstrip()
        # remove the ':' if exists 
        if snippet_split[code_sind].startswith(':'):
            snippet_split[code_sind] = snippet_split[code_sind].lstrip(':')
        else:
            raise ParserError('Bad Syntax. ":" missing in CODE field.')
        code = '\n'.join(snippet_split[code_sind:self.code_eindex+1])
        

        # create the map 
        store = {
            name: {
                'DESC': desc,
                'CODE': code
            }
        }     

        return store
