#!/usr/bin/env python

import PySpectra
import math
import time

def main():
    '''
    simulate a measurement, use setX and setY
    '''
    PySpectra.cls()
    PySpectra.delete()
    
    #PySpectra.setTitle( "sinus, shifted by +1.1")
    sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
    for i in range( sinus.nPts): 
        sinus.setX( i, i/10. + 0.01)
        sinus.setY( i, math.sin( i/10.) + 1.1)
        PySpectra.display( ['sinus'])
        time.sleep( 0.01)

def testDisplayScan_v1(): 
    '''
    using setX and setY
    '''
    PySpectra.cls()
    PySpectra.delete()

    sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', yMin = -1, yMax = 5)
    for i in range( sinus.nPts): 
        sinus.y[i] = math.sin( i/10.) + 1.1
        sinus.currentIndex = i
        PySpectra.display( ['sinus'])
        time.sleep( 0.1)

if __name__ == "__main__":
    testDisplayScan_v1()
    #PySpectra.launchGui()
    
