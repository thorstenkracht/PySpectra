#!/usr/bin/env python

import PySpectra as pysp
import sys

def main():
    pysp.exampleCreate56x3Plots()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()