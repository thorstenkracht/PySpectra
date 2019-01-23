#!/bin/env python

# 1.8.2
import numpy as np

slotList = []

class Slot():
    '''    
    s alot is a container for scans, texts, tags, layouts

    slot
      self.nameSlot
      self.scan
      scan, optional
        self.name == nameSlot, etc.
        self.slot 
      text, optional
        self.nameSlot.I, etc.
      tag, optional
        self.nameSlot.I, etc.
      layout, optional
        self.nameSlot.I, etc.
    '''    

    def __init__( self, name = None):

        global slotList

        if name is None:
            raise ValueError( "GQE.Slot: 'name' is missing")

        self.name = name
        self.scan = None   # to be set the Scan()
        slotList.append( self)
        self.textList = []

    def __del__( self): 
        print "destructing slot", self.name

class Scan():
    '''
    create a scan within a slot
      - a scan contains 2 arrays, x and y, and graphics attributes

    PySpectra.dMgt.GQE.Scan( slot, filename = 'test.fio', x = 1, y = 2)
    PySpectra.dMgt.GQE.Scan( slot, xMin = 0., xMax = 1., np = 11, dType = np.float64)

    '''
    def __init__( self, slot, **kwargs):
        self.name = slot.name
        #
        # if filename is supplied, we read the data
        #
        if 'filename' in kwargs:
            self.readFile( kwargs[ 'filename'])
        else:
            self.createScan( kwargs)
        #
        # the scan knows in which slot it lives, the slot
        # know its members
        #
        self.slot = slot
        slot.scan = self

    def __del__( self):
        print "destructing scan", self.name

    def readFile( self, filename):
        print "Creating a scan by reading a file", filename
        return

    def createScan( self, kwargs):
        '''
        creates a scan using xMin, xMax, np, dType
        '''
        print "Creating a scan using limits", str( kwargs)
        #
        # checking whether all keywards are supplied
        #
        if 'xMin' not in kwargs:
            raise ValueError( "Gqe.Scan: 'xMin' not supplied")
        self.xMin = kwargs[ 'xMin']
        if 'xMax' not in kwargs:
            raise ValueError( "Gqe.Scan: 'xMax' not supplied")
        self.xMax = kwargs[ 'xMax']
        if 'nPts' not in kwargs:
            raise ValueError( "Gqe.Scan: 'nPts' not supplied")
        self.nPts = kwargs[ 'nPts']
        if 'dType' not in kwargs:
            self.dType = np.float64
        else:
            self.dType = np.float64

        delta = (self.xMax - self.xMin)/(self.nPts - 1.)
        self.x = np.arange( self.xMin, self.xMax, delta, dtype = self.dType)
        self.y = np.zeros( self.nPts, dtype = self.dType)

        return
    
        
