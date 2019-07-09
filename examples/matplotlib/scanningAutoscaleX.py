#!/usr/bin/env python
#
# file name: scanningAutoscaleX.py
#

import time
import matplotlib.pyplot as plt
import numpy as np

def display():

    (xMin, xMax, xDelta) = (0., 10., 0.05)

    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(x)

    plt.ion()
    if not plt.get_fignums():
        fig = plt.figure( 1, figsize = (11.6, 8.2))
    else:
        fig = plt.figure(1)
        fig.clear()

    fig.text( 0.5, 0.95, "both axes are auto-scaled", va='center', ha='center')

    ax_tan = fig.add_subplot(1, 1, 1)
    ax_tan.grid( True)
    tan, = ax_tan.plot( x, t, 'b')

    #
    # set_autoscalex_on() seem to have no effect
    #
    # ax_tan.set_autoscalex_on( True)

    for i in range( 1, len(x)):
        tan.set_data(x[0:i], t[0:i])
        ax_tan.set_xlim( x[0], x[i])
        ax_tan.set_ylim( np.min( t[0:i]), np.max( t[0:i]))
        fig.canvas.flush_events()

if __name__ == "__main__":
    display()
