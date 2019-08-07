#!/usr/bin/env python
'''
- each view and item has its own local coordinate system
- viewport and scene coordinates refer to the same thing: 
  QGraphicsView's coordinate system
- coordinates are local to an item
  + logical coordinates not pixels
  + without transformations, 1 logical corrdinate = 1 pixel
- items inherit position and transformation from parent
- zValue is relative to parent
- item transformation does not affect its local coordinate system
- items are painted recursively


- view = QGraphicsView()
  scene = QGraphicsScene( view)
  a scene is a container for graphics items

- t = QTransform()
  t.rotate( 45, Qt.ZAxis)
  t.scale( 1.5, 1.5)
  view.setTransformation( t)
  setTransformationAnchor(...)

- mapFromScene( QPointF)
  maps a point from viewport coordinates to item coordinates, 
  inverse mapToScene( QPointF)
- mapFromItem( QGraphicsItem, QPointF) 
  maps a point from another item's coordinate system to this item's
  inverse: mapToItem( QGraphicsItem, QPointF)

- mapFromParent( QPointF)
  special case 


'''
import pyqtgraph as pg 
from PyQt4 import QtGui 
from PyQt4 import QtCore
import numpy as np 
import sys 
def main(): 
    app = QtGui.QApplication(sys.argv) 
    widg = QtGui.QWidget() 
    widg.move(100, 100) 
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k') 

    pgWidg = pg.GraphicsLayoutWidget()   
    pgWidg.resize(750, 250)  

    plotItem = pgWidg.addPlot(row=1, col=1)
    xt = np.arange( 3., 10., 0.1)
    plotDataItem = plotItem.plot(y= np.tan( xt), x = xt, pen='k') 

    plotItem.addItem(plotDataItem) 
    plotItem.setMouseEnabled(x=False, y=True)

    textItem = pg.TextItem(text = 'A1', color=(0, 0, 0))
    plotItem.addItem(textItem)
    pt = QtCore.QPointF( 0., 0.)
    textItem.setPos(5., 20.)
    print "scenePos", repr( textItem.scenePos())
    print "viewPos", repr( textItem.viewPos())

    for line in dir( plotDataItem):
        print line

    print "mapFromScene", repr( textItem.mapFromScene( pt))
    print "mapToScene", repr( textItem.mapToScene( pt))
    print "plotDataItem, viewPos", repr(plotDataItem.dataBounds( 0))
    print "plotDataItem, viewPos", repr(plotDataItem.dataBounds( 1))

    grid = QtGui.QGridLayout() 
    grid.addWidget(pgWidg, 0,0)          
    widg.setLayout(grid) 
    widg.show() 
    sys.exit(app.exec_()) 

if __name__ == '__main__':  
    main()
