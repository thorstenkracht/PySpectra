#!/usr/bin/env python

import PySpectra
import time, math

def main():
    '''
    scanning in reverse direction
    '''
    PySpectra.cls()
    PySpectra.delete()
    
    sinus = PySpectra.Scan( name = 'sinus', 
                            xMin = 0., xMax = 6.0, nPts = 101, 
                            lineColor = 'red')
    sinus.xMax = 10.
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.setX( i, x)
        sinus.setY( i, math.sin( i/10.))
        PySpectra.display( ['sinus'])
        time.sleep( 0.05)

if __name__ == "__main__":
    main()
    #PySpectra.launchGui()
