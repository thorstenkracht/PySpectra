#!/usr/bin/env python 
'''
a module containing 
derivative(), antiderivative(), yToMinusY()
'''
import PySpectra.GQE as GQE

from numpy import diff as _diff
from scipy import integrate as _integrate
from scipy.optimize import curve_fit as _curve_fit
import bisect as _bisect
import numpy as np
import matplotlib.pyplot as _plt

#def derivativeNumpy( name = None, nameNew = None):
#    '''
#    derivative <scanName> [<newScanName>]
#      calculates the derivative of <scanName> using numpy.diff
#      the result is stored in <newScanName> or <scanName>_derivative
#
#    Returns the created scan
#    '''
#    if name is None:
#        raise ValueError( "calc.derivative: name not specified")
#
#    scan = GQE.getGqe( name)
#    if scan is None:
#        raise ValueError( "calc.derivative: failed to find %s" % name)
#                          
#    # 
#    # the length of diff(a) less than the length of the inputs, by 1
#    # 
#    dydx = _diff( scan.y)/_diff(scan.x)
#    if nameNew is None:
#        temp = "%s_derivative" % scan.name
#    else:
#        temp = nameNew
#    #
#    # shift the x-axis by half of the bin width and ignore the last point
#    #
#    delta = (scan.x[1] - scan.x[0])/2.
#    scan.x = scan.x + delta
#    argout = GQE.Scan( name = temp, x = scan.x[:-1], y = dydx)
#
#    return argout

def derivative( name = None, nameNew = None):
    '''
    derivative <scanName> [<newScanName>]
      calculates the derivative of <scanName> a la spectra
      the result is stored in <newScanName> or <scanName>_derivative

    Returns the created scan
    '''
    if name is None:
        raise ValueError( "calc.derivative: name not specified")

    scan = GQE.getGqe( name)
    if scan is None:
        raise ValueError( "calc.derivative: failed to find %s" % name)

    if nameNew is None:
        temp = "%s_derivative" % scan.name
    else:
        temp = nameNew
    argout = GQE.Scan( name = temp, x = scan.x, y = scan.y)
    argout.currentIndex = scan.currentIndex

    x = np.array( scan.x)
    x = x - x[0]
    y = np.array( scan.y)
    ty = np.array( scan.y)

    npoint = scan.currentIndex + 1

    for i in range( 1, npoint - 1):
      det = (x[i]*x[i+1]*x[i+1] - x[i+1]*x[i]*x[i] - 
             x[i-1]*x[i+1]*x[i+1] + x[i+1]*x[i-1]*x[i-1] + 
             x[i-1]*x[i]*x[i] - x[i]*x[i-1]*x[i-1])
      if det == 0.:
        raise ValueError( "calc.derivative: det == 0.")

      za1 = (y[i]*x[i+1]*x[i+1] - y[i+1]*x[i]*x[i] -
             y[i-1]*x[i+1]*x[i+1] + y[i+1]*x[i-1]*x[i-1] +
             y[i-1]*x[i]*x[i] - y[i]*x[i-1]*x[i-1])
      za2 = (x[i]*y[i+1] - x[i+1]*y[i] -
             x[i-1]*y[i+1] + x[i+1]*y[i-1] +
             x[i-1]*y[i] - x[i]*y[i-1])

      if i == 1:
          ty[0]   = (za1 + 2.0*za2*x[0])/det

      if i == (npoint - 2):
          ty[ npoint - 1] = (za1 + 2.0*za2*x[npoint -1])/det

      ty[i] = (za1 + 2.0*za2*x[i])/det

    for i in range( npoint):
        argout.y[i] = ty[i]

    return argout

#def antiderivativeSciPy(name = None, nameNew = None):
#    '''
#    antiderivative <scanName> [<newScanName>]
#      calculates the anti-derivative of <scanName> using numpy.integrate.trapz
#      the result is stored in <newScanName> or <scanName>_antiderivative
#
#    returns the created scan
#    '''
#    if name is None:
#        raise ValueError( "calc.antiderivative: name not specified")
#
#    scan = GQE.getGqe( name)
#    if scan is None:
#        raise ValueError( "calc.antiderivative: failed to find %s" % name)
#
#    if nameNew is None:
#        temp = "%s_antiderivative" % scan.name
#    else:
#        temp = nameNew
#
#    argout = GQE.Scan( name = temp, x = scan.x, y = scan.y)
#    argout.currentIndex = scan.currentIndex
#    #
#    #  tested the 3 lines below using sin/cosine
#    #
#    for i in range(1, scan.currentIndex + 1):
#        temp = _integrate.trapz( scan.y[:i], scan.x[:i])
#        argout.setY( i - 1, temp)
#
#    argout.yMin = np.min( argout.y)
#    argout.yMax = np.max( argout.y)
#        
#    return argout

def antiderivative( name = None, nameNew = None):
    '''
    antiderivative <scanName> [<newScanName>]
      calculates the anti-derivative of <scanName> a la Spectra
      the result is stored in <newScanName> or <scanName>_antiderivative

    returns the created scan
    '''
    if name is None:
        raise ValueError( "calc.antiderivative: name not specified")

    scan = GQE.getGqe( name)
    if scan is None:
        raise ValueError( "calc.antiderivative: failed to find %s" % name)

    if nameNew is None:
        temp = "%s_antiderivative" % scan.name
    else:
        temp = nameNew

    argout = GQE.Scan( name = temp, x = scan.x, y = scan.y)
    argout.currentIndex = scan.currentIndex
    argout.y[0] = 0.
    for i in range(1, scan.currentIndex + 1):
        dx = float(scan.x[i] - scan.x[i-1])
        argout.y[i] = argout.y[i-1] + (scan.y[i] + scan.y[i-1])*0.5*dx

    argout.yMin = np.min( argout.y)
    argout.yMax = np.max( argout.y)
        
    return argout

def yToMinusY(name = None, nameNew = None):
    '''
    ytominusy <scanName> [<newScanName>]
      the y-values of the new scan are the negative of the scan
      the result is stored in <newScanName> or <scanName>_y2my
    returns the created scan
    '''
    if name is None:
        raise ValueError( "calc.yToMinusY: name not specified")

    scan = GQE.getGqe( name)
    if scan is None:
        raise ValueError( "calc.yToMinusY: failed to find %s" % name)

    if nameNew is None:
        temp = "%s_y2my" % scan.name
    else:
        temp = nameNew

    argout = GQE.Scan( name = temp, nPts = len( scan.y))
    argout.currentIndex = scan.currentIndex
    for i in range( argout.currentIndex + 1): 
        argout.x[i] =  scan.x[i]
        argout.y[i] =  -scan.y[i]

    return argout
