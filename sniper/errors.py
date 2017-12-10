# create exception for parser 
class Error(Exception):
    """
    Root class for the Parser Exception type 
    """
    pass
class ParserError(Error):
    """
    For error in parsing the input 
    """
    def __init__(self, message):
        """
        Constructor 
        """
        self.message = message
class SniperError(Error):
    """
    Encapsulates error which are root 
    """
    def __init__(self, message):
        self.message = message 

class NotImplementedError(Error):
    """
    Encapsulates error which are root 
    """
    def __init__(self, message):
        self.message = message