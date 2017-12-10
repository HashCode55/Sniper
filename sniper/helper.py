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

    def validate_input(self):
        """
        Validates the input of the "new" command.

        params@snippet: snippet as input         
        """
        # trim spaces 
        self.snippet = self.snippet.lstrip()
        # check if the first thing as input is NAME 
        if not self.snippet.startswith('NAME'):            
            raise ParserError('Error Parsing the input.\n')            

    def create_map(self):
        """
        Creates a dict to be stored in json file from the input of 
        "new" command 

        params&snippet: validated snippet 
        returns&dict  : The validated map created
        """
        
