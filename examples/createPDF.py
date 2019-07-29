#!/usr/bin/env python

import PySpectra
import numpy as np

def main(): 
    '''
    create a pdf file
    '''

    PySpectra.cls()
    PySpectra.delete()

    scan = PySpectra.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.)
    
    scan.y = np.sin( scan.x)

    PySpectra.setWsViewport( "DINA4")
    PySpectra.display()

    PySpectra.createPDF()

if __name__ == '__main__': 
    main()
    PySpectra.launchGui()
