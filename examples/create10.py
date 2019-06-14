#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "10 Scans")
    pysp.setComment( "Ein Kommentar")
    for i in range( 10): 
        t = pysp.Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand')
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
