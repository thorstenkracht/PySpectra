#!/bin/env python

class Slot():
    '''    
    s alot is a container for scans, texts, tags, layouts
    '''    

    def __init__( self, name = None):

        if name is None:
            raise ValueError( "Slot: 'name' is missing")
