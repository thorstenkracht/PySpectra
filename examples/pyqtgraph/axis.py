#!/usr/bin/env python
#import sys
#sys.path.insert( 0, "/home/kracht/Misc/pySpectra")

import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui

def set_plotstyle(p1, x_vals, y_vals, style):
    if style == 1:
        axlabel_font = QtGui.QFont()
        axlabel_font.setPixelSize(15)

        p1.showAxis('right')
        p1.showAxis('top')

        p1.showLabel('right', show=False)
        p1.showLabel('top', show=False)

        p1.showGrid(x=False, y=False)
        p1.setLogMode(x=False, y=False)
        p1.getAxis('left').tickFont = axlabel_font
        p1.getAxis('bottom').tickFont = axlabel_font
        p1.getAxis('left').labelFont = axlabel_font
        p1.getAxis('bottom').setHeight(70)
        p1.getAxis('left').setWidth(100)
        p1.getAxis('right').setWidth(60)
        #p1.getAxis('left').setStyle(tickTextOffset=15)
        #p1.getAxis('bottom').setStyle(tickTextOffset=15)
        #p1.getAxis('top').setStyle( showValues = False)
        #p1.getAxis('top').showValues=False
        p1.getAxis('top').style[ 'showValues'] = False

        ax = p1.getAxis('bottom')
        dx = [(value, '{:.1f}'.format(value)) for value in x_vals]
        ax.setTicks([dx, []])

        ay = p1.getAxis('left') 
        dy = [(value, '{:.1f}'.format(value)) for value in y_vals]
        ay.setTicks([dy, []])
    return p1

app = pg.mkQApp()

pw = pg.PlotWidget(title="Example")
x = np.arange(7)
y = x**2/150
pw.plot(x=x, y=y, symbol='o')
pw.show()
pw.setWindowTitle('Example')
set_plotstyle(pw, x, y, 1)


if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
