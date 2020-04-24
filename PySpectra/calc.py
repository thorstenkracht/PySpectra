#!/usr/bin/env python 
'''
a module containing 
derivative(), antiderivative(), yToMinusY()
'''
import GQE 

from numpy import diff as _diff
from scipy import integrate as _integrate
import numpy as np

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
        raise ValueError( "calc.yToMinus: failed to find %s" % name)

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
  
def ssa( xIn, yIn, flagNbs = False, stbr = 3):
    '''
    performs a simple scan analysis
    input: 
      xIn, yIn, numpy arrays 
      flagNbs,  if True, no background subtraction
      stbr,     signal to background ratio
    returns: 
      dct['status']
      dct['reason']   0: ok, 1: np < 6, 2: stbr, 3: no y(i) > 0., 
                      4, 5: midpoint calc, 6: max outside x-range
                      7: not numpy array
      dct['cms']      center of mass
      dct['integral'] 
      dct['midpoint'] midpoint
      dct['fwhm'] 
      dct['peak_x']  
      dct['peak_y']
      dct['back_int'] background integral
      dct['r_back']   right background
      dct['l_back']   left background

    '''

    reason2String = { '0': 'ok', 
                      '1': 'np < 6', 
                      '2': 'signal-to-background', 
                      '3': 'no y(i) > 0', 
                      '4': 'midpoint calc.', 
                      '5': 'midpoint calc.', 
                      '6': 'maximum outside x-range', 
                      '7': 'not a numpy array'}
    status = 1
    reason = 0
    dct = {}

    dct['status'] = status
    dct['reason'] = reason
    dct['reasonString'] = reason2String[ str( dct['reason'])] 
    dct['cms'] = 0
    dct['integral'] = 0
    dct['midpoint'] = 0
    dct['fwhm'] = 0
    dct['peak_x'] = 0
    dct['peak_y'] = 0
    dct['back_int'] = 0
    dct['r_back'] = 0
    dct['l_back'] = 0

    if( type( xIn).__name__ != 'ndarray' or type( yIn).__name__ != 'ndarray'): 
        dct['status'] = 0
        dct['reason'] = 7
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct
        
    if( xIn[-1] > xIn[0]):
        x = np.copy( xIn)
        y = np.copy( yIn)
    else:
        x = np.copy( xIn)
        y = np.copy( yIn)
        #
        # revert a numpy array
        #
        x = x[::-1]
        y = y[::-1]

    if len(x) < 6:
        dct['status'] = 0
        dct['reason'] = 1
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct

    b_back = 0
    a_back = 0
    n = len(x)
    y_max = y.max()
    if not flagNbs:
        n_back = len(x)/10
        if n_back < 2:
            n_back = 2
        if n_back > 20:
            n_back = 20

        x_sum  = 0.0 
        xx_sum = 0.0 
        xy_sum = 0.0   
        y_sum  = 0.0  
  
        for i in range( n_back):
            x_sum = x_sum + x[i] + x[n - 1 - i]
            xx_sum = xx_sum + x[i]*x[i] + x[n - 1 - i]*x[n - 1 - i]
            xy_sum = xy_sum + x[i]*y[i] + x[n - 1 - i]*y[n - 1 - i]
            y_sum = y_sum + y[i] + y[ n - 1 - i]      

        if (2.0*n_back*xx_sum-x_sum*x_sum) != 0.:
            b_back = (y_sum*xx_sum-xy_sum*x_sum)/(2.0*n_back*xx_sum-x_sum*x_sum)
            a_back = (2.0*n_back*xy_sum-y_sum*x_sum)/(2.0*n_back*xx_sum-x_sum*x_sum)
  
    back_int = (0.5*a_back*(x[n - 1]+x[0])+b_back)*(x[n - 1]-x[0])
    l_back = a_back*x[0]      + b_back
    r_back = a_back*x[n - 1]   + b_back  

    #
    #    the maximum has to exceed the background by a factor of stbr
    #
    if( stbr*r_back > y_max or stbr*l_back > y_max):
        dct['status'] = 0
        dct['reason'] = 2
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct

    #
    # BACKGROUND 
    #
    for i in range( n):
        y[i] = y[i] - a_back*x[i] - b_back

    #
    # FIND PEAK POSITION, PEAK INTENSITY AND PEAK INDEX                        
    #
  
    peak_x     = 0.0
    peak_y     = 0.0
    peak_index = 0
  
    flag = 0
    for i in range( n):
        if (y[i] > peak_y):
            peak_y = y[i]
            peak_x = x[i]
            peak_index = i
            flag = 1
  
    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 3 # no y > 0
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct

    #
    # DETERMINE FWHM AND MIDPOINT                                                */
    #
    x_left  = 0.0
    x_right = 0.0
    
    flag    = 0
    for i in range( n):
        if (peak_index + i) >= n:
            break
        if y[peak_index+i] < 0.5*peak_y:
            temp   = (0.5*peak_y-y[peak_index+i-1])/(y[peak_index+i-1]-y[peak_index+i])
            x_right = x[peak_index+i-1]+temp*(x[peak_index+i-1]-x[peak_index+i])
            i = n - 1
            flag = 1
            break

    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 4 # midpoint calc failed
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct
  
    flag = 0
    for i in range( n):
        if (peak_index - i) < 0:
            break
        if (y[peak_index-i] < 0.5*peak_y):
            temp   = (y[peak_index-i+1]-0.5*peak_y)/(y[peak_index-i+1]-y[peak_index-i])
            x_left = x[peak_index-i+1] - temp*(x[peak_index-i+1]-x[peak_index-i])
            i = n - 1
            flag = 1
            break

    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 5  # midpoint calc failed 
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct

    fwhm     =  x_right-x_left
    midpoint = 0.5*(x_right+x_left)
  
    #
    # CALCULATE SCAN INTEGRAL AND CENTER OF MASS  
    #  
    scan_int = 0.0
    cms      = 0.0
  
    for i in range( n - 1):
        scan_int = scan_int + (y[i]+y[i+1])*0.5*(x[i+1]-x[i])
        cms      = cms      + (y[i]+y[i+1])*0.5*(x[i]+x[i+1])*0.5*(x[i+1]-x[i])

    cms = cms / scan_int

    #
    # b2 bug: cms was outside the x-interval
    # 
    if( cms < x[0] or cms > x[-1] or
      midpoint < x[0] or midpoint > x[-1] or
      peak_x < x[0] or peak_x > x[-1]):
        dct['status'] = 0
        dct['reason'] = 6 # max outside x-interval 
        dct['reasonString'] = reason2String[ str(dct['reason'])]
        return dct

    dct['status'] = status
    dct['reason'] = reason
    dct['cms'] = cms
    dct['integral'] = scan_int
    dct['midpoint'] = midpoint
    dct['fwhm'] = fwhm
    dct['peak_x'] = peak_x
    dct['peak_y'] = peak_y
    dct['back_int'] = back_int
    dct['r_back'] = r_back
    dct['l_back'] = l_back
    
    return dct
