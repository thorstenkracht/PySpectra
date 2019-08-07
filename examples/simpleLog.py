#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "A simple plot")
    pysp.setComment( "here would be a comment")
    g = pysp.Scan( name = "linear", 
                   xMin = 0.01, xMax = 5., nPts = 101, 
                   xLabel = "Position", yLabel = 'Signal', 
                   yLog = True, 
                   lineColor = 'red')
    g.y *= 10.
    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
