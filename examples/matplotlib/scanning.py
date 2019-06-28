#!/usr/bin/env python
#
# file name: mpl_scan.py
#

import time
import matplotlib.pyplot as plt
import numpy as np

dt = None
ax_dt = None

def display():
    global dt, ax_dt 

    xMin = 0
    xMax = 50
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(x)
    tm = range( len(t))

    plt.ion()
    if not plt.get_fignums():
        fig = plt.figure( 1, figsize = (11.6, 8.2))
    else:
        fig = plt.figure(1)
        fig.clear()

    fig.text( 0.5, 0.95, "A figure containing two plots", va='center', ha='center')

    ax_tan = fig.add_subplot(2, 1, 1)
    ax_tan.grid( True)
    ax_tan.set_autoscale_on( True)
    ax_tan.set_xlabel( 'Phase')
    ax_tan.set_ylabel( 'tan')
    ax_tan.set_title( 'the tan() function')
    tan, = ax_tan.plot( x, t, 'b')
    ax_tan.set_xlim( xmin=x[0], xmax=x[-1])

    ax_dt = fig.add_subplot(212)
    ax_dt.grid( True)
    ax_dt.set_autoscaley_on( True)
    ax_dt.set_xlabel( 'no. of display calls')
    ax_dt.set_ylabel( 'time[s]')
    ax_dt.set_title( 'time to display various lenths of both plots')
    dt, = ax_dt.plot( x, tm, 'r')
    ax_dt.set_xlim( 0, len( x) - 1)

    tm = []
    start = time.time()
    for i in range( 1, len(x)):
        tan.set_data(x[0:i], t[0:i])
        ax_tan.set_ylim( np.min( t[0:i]), np.max( t[0:i]))
        tm.append( time.time() - start)
        start = time.time()
        dt.set_data(range(i), tm[0:i])
        ax_dt.relim()
        ax_dt.autoscale_view(True,False,True)
        fig.canvas.flush_events()
        #plt.pause( 0.001)
        #plt.draw()

if __name__ == "__main__":
    display()
