#!/usr/bin/env python
#
# file name: scanningReverse.py
#

import time
import matplotlib.pyplot as plt
import numpy as np

def display():

    (xMin, xMax, xDelta)  = (0., 10., 0.1)
    x = np.arange( xMin, xMax, xDelta)
    x = x[::-1]
    t = np.tan(x)

    plt.ion()
    if not plt.get_fignums():
        fig = plt.figure( 1, figsize = (11.6, 8.2))
    else:
        fig = plt.figure(1)
        fig.clear()

    tan_ax = fig.add_subplot(1, 1, 1)
    tan_ax.grid( True)
    tan_ax.set_xlabel( 'Phase')
    tan_ax.set_ylabel( 'tan')
    tan_ax.set_title( 'the tan() function')
    tan, = tan_ax.plot( x, t, 'b')
    tan_ax.set_xlim( xMin, xMax)
    
    for i in range( 1, len(x)):
        tan.set_data(x[0:i], t[0:i])
        tan_ax.set_ylim( np.min( t[0:i]), np.max( t[0:i]))
        fig.canvas.flush_events()

if __name__ == "__main__":
    display()
