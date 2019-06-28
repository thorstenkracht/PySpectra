#!/usr/bin/env python
#
# file name: mpl_scan.py
#

from sardana.macroserver.macro import macro, Type
import time, sys
import matplotlib.pyplot as plt
import numpy as np

dt = None
ax_dt = None

def display():
    global dt, ax_dt 

    xMin = 0
    xMax = 20
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    t = np.sin(x)

    #plt.ion()
    if not plt.get_fignums():
        fig = plt.figure( 1, figsize = (11.6, 8.2))
    else:
        fig = plt.figure(1)
        fig.clear()

    fig.text( 0.5, 0.95, "A figure containing two plots", va='center', ha='center')

    ax_sin = fig.add_subplot(1, 1, 1)
    ax_sin.grid( True)
    ax_sin.set_autoscale_on( True)
    ax_sin.set_xlabel( 'Phase')
    ax_sin.set_ylabel( 'sin')
    ax_sin.set_title( 'the sin() function')
    sin, = ax_sin.plot( x, t, marker = 'o', color='red')
    ax_sin.set_xlim( xmin=x[0], xmax=x[-1])

    plt.show()

    print "Prtc ",
    sys.stdin.readline()

if __name__ == "__main__":
    display()
