#!/usr/bin/env python

import PySpectra as pysp
import sys

def main():
    pysp.example_SimplePlot()
    sys.stdout.write( "Prtc")
    sys.stdout.flush()

    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()
