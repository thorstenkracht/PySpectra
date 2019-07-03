#!/usr/bin/env python

import PySpectra
import numpy as np

def main(): 
    '''
    
    '''
    print "testGrphics.testLissayous"

    PySpectra.setWsViewport( "DINA5S")
    
    PySpectra.cls()
    PySpectra.delete()
    scan = PySpectra.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)
    
    x  = np.linspace( 0., 6.5, 1000)
    y  = np.linspace( 0., 6.5, 1000)
    
    scan.x = np.cos( x)
    scan.y = np.sin( y)
    
    PySpectra.display()
    
    for i in range( 1500):
        x = x + 0.005
        scan.plotDataItem.setData(np.cos( x), np.sin( y))
        PySpectra.processEvents()
        

if __name__ == '__main__': 
    main()
    PySpectra.launchGui()
