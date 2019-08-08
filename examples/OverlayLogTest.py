#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "2 Overlay Scans, with log scale")
    g1 = pysp.Scan( name = "gauss", xMin = 0.1, xMax = 10., yLog = True, nPts = 101, lineColor = 'red')

    g2 = pysp.Scan( name = "gauss2", xMin = 0, xMax = 100, yLog = False,
                    nPts = 101, lineColor = 'green')

    pysp.overlay( "gauss2", "gauss")

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
