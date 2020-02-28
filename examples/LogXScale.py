#!/usr/bin/env python

import PySpectra as pysp
import sys

def main():
    pysp.example_LogXScale()
    sys.stdout.write( "Prtc")
    sys.stdout.flush()
    print "Prtc ",
    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()

