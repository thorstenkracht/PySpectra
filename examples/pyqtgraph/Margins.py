#!/usr/bin/env python

from pyqtgraph.Qt import QtGui, QtCore                                              
import pyqtgraph as pg                                                              

app = QtGui.QApplication([])                                                        
view = pg.GraphicsView()                                                            
l = pg.GraphicsLayout(border='g')                                                   
view.setCentralItem(l)                                                              
view.show()                                                                         
view.resize(800,600)                                                                

l.addPlot(0, 0)                                                                     
l.addPlot(1, 0)                                                                     

l.layout.setSpacing(0.)                                                             
l.setContentsMargins( 0., 0., 0., 0.)                                                

if __name__ == '__main__':                                                          
    import sys                                                                      
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):         
        QtGui.QApplication.instance().exec_() 
