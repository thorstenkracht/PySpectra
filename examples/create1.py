#!/usr/bin/env python

import PySpectra as pysp
import numpy as np

def main():
    pysp.cls()
    pysp.delete()
    pysp.setTitle( "Ein Titel")
    pysp.setComment( "Sinus(), nach oben verschoben")
    t1 = pysp.Scan( name = "t1", xMin = 0.01, xMax = 10., nPts = 101, lineColor = 'blue', yLabel = 'sin')
    t1.addText( text = "a left/center aligned text", x = 0.05, y = 0.8, hAlign = 'left', vAlign = 'center')
    t1.addText( text = "a right/centeraligned text", x = 0.95, y = 0.8, hAlign = 'right', vAlign = 'center')
    t1.addText( text = "a center/top aligned text, red, fontSize: 10", x = 0.5, y = 0.5, hAlign = 'center', 
                vAlign = 'top', fontSize=10, color = 'red')
    t1.addText( text = "a center/center aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'center')
    t1.addText( text = "a center/bottom aligned text", x = 0.5, y = 0.5, hAlign = 'center', vAlign = 'bottom')
    t1.y = np.sin( t1.x) + 1.001

    pysp.display()

if __name__ == '__main__': 
    main()
    pysp.launchGui()
