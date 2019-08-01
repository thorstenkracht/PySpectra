#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "2 Overlay Scans, with log scale")
    g1 = pysp.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
    mu = 0.
    sigma = 1.
    g1.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g1.y-mu)**2/(2.*sigma**2))
    g2 = pysp.Scan( name = "gauss2", xMin = -5., xMax = 5., yLog = False,
                    nPts = 101, lineColor = 'green')
    mu = 0.5
    sigma = 1.2
    g2.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g2.y-mu)**2/(2.*sigma**2))

    pysp.overlay( "gauss2", "gauss")

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
