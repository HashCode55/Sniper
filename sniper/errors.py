"""
Errors for Sniper

author: HashCode55
data  : 9/12/17
"""

import sys 
import inspect 

# create exception for parser 
class Error(Exception):
    """
    Root class for the Parser Exception type 
    """
    def __init__(self, message):
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__} (line {1}): {2}".format(type(self), ln, message),
        sys.exit(self)

class ParserError(Error):
    """
    For error in parsing the input 
    """
    pass 
    
class SniperError(Error):
    """
    Encapsulates error which are root 
    """
    pass

class NotImplementedError(Error):
    """
    Encapsulates error which are root 
    """
    pass