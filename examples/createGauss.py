#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "This is a title")
    pysp.setComment( "Die Normalverteilung")
    g = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
    mu = 0.
    sigma = 1.
    g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2*sigma**2))

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
