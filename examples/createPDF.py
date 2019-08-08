#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import sys

def main():
    pysp.exampleCreatePDF()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()


#!/usr/bin/env python

import PySpectra
import numpy as np

def main(): 
    '''
    create a pdf file
    '''

    PySpectra.cls()
    PySpectra.delete()

    scan = PySpectra.Scan( name = 'PDF Output', nPts = 100, xMin = -1., xMax = 1.,
                           xLabel = 'Position', yLabel = "Counts")
    
    scan.y = np.sin( scan.x)

    PySpectra.setWsViewport( "DINA4")
    PySpectra.display()

    PySpectra.createPDF( flagPrint = True)

if __name__ == '__main__': 
    main()
    PySpectra.launchGui()
