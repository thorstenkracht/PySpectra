#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Ein Kommentar")
    t1 = pysp.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = pysp.Scan( "t2", yLabel = 'cos', symbol = '+')
    t2.y = np.cos( t2.x)
    t3 = pysp.Scan( name = "t3", lineColor = 'green', yLabel = 'tan')
    t3.y = np.tan( t3.x)
    t4 = pysp.Scan( name = "t4", lineColor = 'NONE', yLabel = 'random', symbol = '+', symbolColor = 'CYAN')
    t4.y = np.random.random_sample( (len( t4.y), ))
    t5 = pysp.Scan( name = "t5", lineColor = 'magenta', yLabel = 'x**2')
    t5.y = t5.x * t5.x
    pysp.overlay( 't5', 't3')
    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
