#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import sys

def main():
    pysp.exampleScanningReverse()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()
