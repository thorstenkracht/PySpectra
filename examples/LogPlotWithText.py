#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import sys

def main():
    pysp.cls()
    pysp.delete()
    t1 = pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, 
                     lineColor = 'blue', xLabel='Position', yLabel = 'signal', yLog = True)
    t1.addText( text = "a left/center aligned text, should be in the center", 
                x = 0.05, y = 0.5, hAlign = 'left', vAlign = 'center')
    pysp.display()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()
