#!/bin/env python
'''
python ./test/examples/testExamples.py testExamples.test_execTests
'''
import sys
import PySpectra
import numpy as np
import unittest
import time, sys, os
import math 

class testExamples( unittest.TestCase):

    def test_execTests( self):
        '''
        
        '''
        PySpectra.example1ScanWithTexts()
        PySpectra.procEventsLoop( 1)

        PySpectra.example22Scans()
        PySpectra.procEventsLoop( 1)

        PySpectra.example2GaussOverlaidWithLog()
        PySpectra.procEventsLoop( 1)

        PySpectra.example2OverlaidDoty()
        PySpectra.procEventsLoop( 1)

        PySpectra.example3WithTextContainer()
        PySpectra.procEventsLoop( 1)

        PySpectra.example56Scans()
        PySpectra.procEventsLoop( 1)

        PySpectra.example5Scans()
        PySpectra.procEventsLoop( 1)

        PySpectra.exampleGauss()
        PySpectra.procEventsLoop( 1)

        PySpectra.exampleGaussAndSinusOverlaid()
        PySpectra.procEventsLoop( 1)

        PySpectra.exampleScanning()
        PySpectra.procEventsLoop( 1)
 
        
if __name__ == "__main__":
    unittest.main()
