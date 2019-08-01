#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Overlay 2 Scans")
    pysp.setComment( "no comment")
    g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2.*sigma**2))
    t1 = pysp.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                    yMin = -1.5, yMax = 1.5, yLabel = 'sin')
    t1.y = np.sin( t1.x)
    pysp.overlay( "sinus", "gauss")
    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
