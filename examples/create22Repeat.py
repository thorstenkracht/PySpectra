#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import sys

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "22 Scans")
    for i in range( 22): 
        t = pysp.Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand', 
                       autoscaleX = True, autoscaleY = True)
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()
    print "Prtc ",
    sys.stdin.readline()

    pysp.cls()
    pysp.delete()
    pysp.setTitle( "22 Scans, repeated")
    for i in range( 22): 
        t = pysp.Scan( name = "t%d" % i, lineColor = 'blue', yLabel = 'rand', 
                       autoscaleX = True, autoscaleY = True)
        t.y = np.random.random_sample( (len( t.x), ))
    pysp.display()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()
