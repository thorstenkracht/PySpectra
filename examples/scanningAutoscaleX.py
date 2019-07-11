#!/usr/bin/env python

import PySpectra
import math
import time

def main():
    '''
    using setX and setY
    '''
    PySpectra.cls()
    PySpectra.delete()

    sinus = PySpectra.Scan( name = 'sinus', 
                            xMin = 0., xMax = 6.0, nPts = 101, 
                            autoscaleX = True, 
                            lineColor = 'red', yMin = -1.2, yMax = 1.2)
    for i in range( sinus.nPts): 
        sinus.y[i] = math.sin( i/10.) 
        sinus.currentIndex = i
        PySpectra.display()
        time.sleep( 0.05)

if __name__ == "__main__":
    main()
    #PySpectra.launchGui()
    
