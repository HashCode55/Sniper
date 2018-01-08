"""
Version of the package

author: HashCode55
data  : 09/12/2017
"""

class Version(object):
    """Version of the package"""    
    def __setattr__(self, *args):
        raise TypeError("can't modify immutable instance")
    __delattr__ = __setattr__

    def __init__(self, num):
        super(Version, self).__setattr__('number', num)

