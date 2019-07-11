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
                            autoscaleX = True, 
                            lineColor = 'red')
    for i in range( sinus.nPts): 
        x = 10. - i/10.
        sinus.x[i] = x
        sinus.y[i] = math.sin( i/10.)
        sinus.currentIndex = i
        PySpectra.display( ['sinus'])
        time.sleep( 0.02)

if __name__ == "__main__":
    main()
    #PySpectra.launchGui()
