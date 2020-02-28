#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import sys

def main():
    pysp.example_Create22Plots()
    sys.stdout.write( "Prtc")
    sys.stdout.flush()

    sys.stdin.readline()

if __name__ == '__main__': 
    main()
    #pysp.launchGui()
