#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Ein Kommentar")
    textScan = pysp.Scan( name = "textContainer", textOnly = True)
    textScan.addText( text = "some information", 
                      x = 0., y = 0.95, color = 'blue')
    textScan.addText( text = "and more infos", 
                      x = 0., y = 0.85, color = 'blue')
    t1 = pysp.Scan( name = "t1", lineColor = 'blue', yLabel = 'sin')
    t1.y = np.sin( t1.x)
    t2 = pysp.Scan( "t2", yLabel = 'cos', symbol = 'o', symbolColor = 'red', symbolSize = 5)
    t2.y = np.cos( t2.x)
    t3 = pysp.Scan( "t3", yLabel = 'tan', symbol = '+', lineColor = 'cyan', symbolColor = 'green', symbolSize = 5)
    t3.y = np.tan( t3.x)

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
