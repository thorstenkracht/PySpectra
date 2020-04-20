#!/usr/bin/env python

import PySpectra as pysp
import numpy as np
import time

def main():
    t1 = pysp.Scan( name = "t1", color = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t1.currentIndex = 10
    
    t2 = pysp.Scan( name = "t2", color = 'blue', yLabel = 'rand')
    t2.y = np.random.random_sample( (len( t2.x), ))
    
    for i in range( 10, len( t1.x)):
        t1.currentIndex = i
        pysp.display()
        t2.y = np.random.random_sample( (len( t2.x), ))
        t2.lastIndex = 0

    pysp.processEventsLoop()
    
if __name__ == "__main__":
    main()    
