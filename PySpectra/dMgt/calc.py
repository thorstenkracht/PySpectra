#!/usr/bin/env

import GQE as _GQE
from numpy import diff
from scipy import integrate as _integrate

def derivative( name = None, nameNew = None):
    '''
    derivative <scanName> [<newScanName>]
      calculates the derivative of <scanName> using numpy.diff
      the result is stored in <newScanName> or <scanName>_derivative

    Returns the created scan
    '''
    if name is None:
        raise ValueError( "calc.derivative: name not specified")

    scan = _GQE.getScan( name)
    if scan is None:
        raise ValueError( "calc.derivative: failed to find %s" % name)
                          
    dydx = diff( scan.y)/diff(scan.x)
    if nameNew is None:
        temp = "%s_derivative" % scan.name
    else:
        temp = nameNew
    argout = _GQE.Scan( name = temp, nPts = len( dydx))
    argout.x = scan.x
    argout.y = dydx
    return argout

def antiderivative(name = None, nameNew = None):
    '''
    antiderivative <scanName> [<newScanName>]
      calculates the anti-derivative of <scanName> using numpy.integrate.trapz
      the result is stored in <newScanName> or <scanName>_antiderivative

    returns the created scan
    '''
    if name is None:
        raise ValueError( "calc.antiderivative: name not specified")

    scan = _GQE.getScan( name)
    if scan is None:
        raise ValueError( "calc.antiderivative: failed to find %s" % name)

    if nameNew is None:
        temp = "%s_antiderivative" % scan.name
    else:
        temp = nameNew

    argout = _GQE.Scan( name = temp, nPts = len( scan.y))

    argout.y[0] = 0.
    for i in range(1, len( scan.x)):
        argout.y[i] = _integrate.trapz( scan.y[:i], scan.x[:i])

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

    scan = _GQE.getScan( name)
    if scan is None:
        raise ValueError( "calc.yToMinus: failed to find %s" % name)

    if nameNew is None:
        temp = "%s_y2my" % scan.name
    else:
        temp = nameNew

    argout = _GQE.Scan( name = temp, nPts = len( scan.y))

    argout.y = - scan.y[:]

    return argout
