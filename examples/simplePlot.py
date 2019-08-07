#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "A simple plot")
    pysp.setComment( "here would be a comment")
    g = pysp.Scan( name = "gauss", 
                   xMin = -5., xMax = 5., nPts = 101, 
                   xLabel = "Position", yLabel = 'Signal', 
                   lineColor = 'red')
    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
