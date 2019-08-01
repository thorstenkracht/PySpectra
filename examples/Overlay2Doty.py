#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "2 Overlaid Scans")
    t1 = pysp.Scan( name = "t1", xMin = 0, xMax = 10, nPts = 101, lineColor = 'blue', 
               yLabel = 'sin', doty = True)
    t1.y = np.sin( t1.x)
    t2 = pysp.Scan( "t2", yLabel = 'cos', xMin = 0, xMax = 10, nPts = 101, lineColor = 'green', doty = True)
    t2.y = np.cos( t2.x)
    t2.overlay = "t1"

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
