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
    ssa() - simple scan analysis function 
      code also in 
      /home/kracht/Misc/Sardana/hasyutils/HasyUtils/ssa.py

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

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 18:02:40 2015

@author: sprung
"""
# --------------------------------------------------------------------------- #
def fastscananalysis(x,y,mode):
    """Fast scan analysis
    # ---
    # --- Input variables:
    # --- x       : vector of motor positions
    # --- y       : vector of intensity values
    # --- mode    : supported "PEAK","CMS","CEN","DIP","DIPM","DIPC","STEP","STEPM","STEPC"
    # ---
    # --- Output variables:
    # --- xpos    : "goal" motor position according to the chosen mode
    # --- xpeak   :  motor position of the peak value 
    # --- xcms    :  motor position of the center of mass
    # --- xcen    :  motor position of the gaussian fit
    # --- message :  some message string
    # ---
    # --- Version 03 by MS and AZ 20150209
    # ---
    """
    # --- Debug switch
    debug   = 0
    
    # --- Convert "x" and "y" to NUMPY arrays
    x = np.array(x)
    y = np.array(y)

    # --- Predefine output variables
    message = "undefined"
    xpos    = np.mean(x)
    xpeak   = np.mean(x)
    xcms    = np.mean(x)
    xcen    = np.mean(x)

    # --- Check input variable "mode"
    if not mode.lower() in [ "peak", "cen", "cms", "dip", "dipc", "dipm",
                             "step", "stepc", "stepm", "slit", "slitc", "slitm"]:
        if debug == 1:    
            print( "Scan analysis MODE not specified!\n Possible modes: peak, cen, cms, dip, dipc, dipm, step, stepc and stepm, slit, slitc and slitm!")
            return message, xpos, xpeak, xcen, xcms
        mode = "peak"            

    # --- Check input variables "x" and "y"
    minpoints = 9
    if len(x) < minpoints or len(y) < minpoints:
        message = 'Not enough scan data points. Please scan over at least 9 points!'
        return message, xpos, xpeak, xcen, xcms
    if len(x) != len(y):
        message = 'Error: Input vectors are not of identical length!'
        return message, xpos, xpeak, xcen, xcms

    # --- Prepare x and y according to mode selection
    if mode.lower() == "peak" or mode.lower() == "cms" or mode.lower() == "cen":
        y = y - np.nanmin(y)            # --- remove constant offset
        
    if mode.lower() == "dip" or mode.lower() == "dipc" or mode.lower() == "dipm":
        y = -y                          # --- invert the data
        y = y - np.nanmin(y)            # --- remove constant offset
        
    if mode.lower() == "step" or mode.lower() == "stepc" or mode.lower() == "stepm":
        if y[0] > y[-1]:                # --- this is a negative slit scan
            y = -y                      # --- invert the data
        y = _deriv(y)                    # --- calculate derivative of signal of identical length
        y = y - np.nanmin(y)            # --- remove constant offset

    if mode.lower() == "slit" or mode.lower() == "slitc" or mode.lower() == "slitm":
        # --- Good cases: a) constant plus slope up   & b) slope down plus constant
        # --- Bad  cases: c) constant plus slope down & d) slope up plus constant
        SmoothWidth, SmoothType, Ends = (5, 3, 0)
        # dy = _deriv(y)                                                           #--- calculate 1st derivative of signal
        dy = _fastsmooth( _deriv(y), SmoothWidth, SmoothType, Ends)                #--- calculate 1st derivative of signal
        if y[0] > y[-1] and np.mean(dy[0:2]) > np.mean(dy[-3:-1]): # --- case c)
            y = -y                      # --- invert the data
        if y[0] < y[-1] and np.mean(dy[0:2]) > np.mean(dy[-3:-1]): # --- case d)
            y = -y                      # --- invert the data
        # y = _deriv( _deriv(y))                                                     # --- calculate 2nd derivative of signal of identical length
        # y = _deriv( _fastsmooth( _deriv(y), SmoothWidth, SmoothType, Ends))          # --- calculate 2nd derivative of signal of identical length
        y = _fastsmooth( _deriv( _deriv(y)), SmoothWidth, SmoothType, Ends)          #--- calculate 2nd derivative of signal of identical length
        y = y - np.nanmin(y)            # --- remove constant offset

    # --- Check if intensity signal contains a peak
    # --- Returns also an estimate for a possible peak index & peak width
    ispeak, peaki, peakw = _check4peak(x,y)
    if ispeak == 0:
        message = 'Error %s: No peak found in data!' % mode.upper()
        return message, xpos, xpeak, xcen, xcms

    # --- Pre-evaluate the data
    imax  = np.argmax(y)                   # --- index of maximum value (for peak, dip, step)
    ip    = peaki
    if debug == 1:
        print( 'Indices: %d %d' % ( imax, ip))
    yl    = y[:ip+1]                       # --- Intensity left  side
    yr    = y[ip:]                         # --- Intensity right side
    hl    = np.amax(yl)- np.amin(yl)       # --- Intensity difference left  side
    hr    = np.amax(yr)- np.amin(yr)       # --- Intensity difference right side

    # --- Some 'Return' conditions
    if imax <= 1 or imax >= len(y) - 1: # --- Position of peak, dip or step at the far edge of the scan range
        message = 'Error %s: Estimated position at the far edge of the scan range. Please use a larger scan range!' % mode.upper()
        return message, xpos, xpeak, xcen, xcms

    # --- One side of the peak is MUCH higher than the other
    # --- The 'real' peak might be out of the scan range
    minlevel = 0.90
    if abs(hl-hr) >= minlevel * max(hl,hr): 
        message = 'Error %s: One side of the peak is much higher than the other! Please use a larger scan range!' % mode.upper()
        return message, xpos, xpeak, xcen, xcms

    # --- Symmetrize/Reduce data points for Gaussian fitting (cen, dipc, stepc)
    # --- (if peak is not measured completely)
    xf          = x
    yf          = y
    yfmax       = np.amax(y)
    yfmin       = np.amin(y)
    sigma_start = peakw
    if abs(hl-hr) <= minlevel * max(hl,hr) and abs(hl-hr) >= 0.40 * max(hl,hr):# --- One side of the peak is not fully measured
        if hl >= hr:                                                           # --- Use the higher (better) side for fitting
            yfmax  = np.amax(yl)
            yfmin  = np.amin(yl)
        else:
            yfmax  = np.amax(yr)
            yfmin  = np.amin(yr)

    # --- Symmetrize/Reduce data points for CMS calculation (cms, dipm, stepm)
    xm = x
    ym = y
    if abs(hl-hr) >= 0.025 * max(hl,hr):                       # --- One side of the peak is not fully measured or has a higher background
        if hl > hr:
            try:
                ind = _bisect.bisect(yl, np.amin(yr))           # --- Returns the index of the first element of yl greater than the minimum of yr 
            except:
                ind = 0
            if ind < 0 or ind > len(xm):
                ind = 0
            if debug == 1:
                print( "%s %s %s %s %s" % (repr(hl), repr( hr), repr( len(xm)), repr( imax), repr( ind)))
            xm = x[ind:]
            ym = y[ind:]
        else:
            try:
                ind = imax + _bisect.bisect(-yr, -np.amin(yl))  # --- Returns the index of the first element of -yr greater than the negative minimum of yl 
            except:
                ind = len(xm)
            if ind < 0 or ind > len(xm):
                ind = len(xm)
            if debug == 1:
                print( "%s %s %s %s %s" % (repr(hl), repr( hr), repr( len(xm)), repr( imax), repr( ind)))
            xm = x[:ind]
            ym = y[:ind]

    # --- Calulating the goal position according to mode
    xpeak = x[imax]
    xcms  = _center_of_mass(xm,ym)
    if debug == 2:
        print( "%s" % repr( xcms))
    p0    = [yfmin, yfmax-yfmin, x[imax], sigma_start]
    npara = len(p0)
    #
    # 29.8.2017: try-except fixes the bug discovered by Florian Bertram
    #
    try:
        coeff, var_matrix = _curve_fit( _gauss, xf, yf, p0=p0)
    except: 
        message = 'Error: trapped exception from _curve_fit'
        return message, xpos, xpeak, xcen, xcms
        
    chi_2 = _chi2(npara, yf, _gauss(xf,*coeff))
    xcen  = coeff[2]

    # --- Output meassges
    if debug == 1:
        # --- Positive signals
        if mode.lower() == "peak" or mode.lower() == "cms" or mode.lower() == "cen":
            print( "Position of Peak: %s" % xpeak)
            print( "Position of CMS : %s" % xcms)
            print( "Position of CEN : %.7f" % xcen)
        # --- Negative signals
        if mode.lower() == "dip" or mode.lower() == "dipm" or mode.lower() == "dipc":
            print( "Position of DIP : %s" % xpeak)
            print( "Position of DIPM: %s" % xcms)
            print( "Position of DIPC: %s" % xcen)
        # --- Step-like signals
        if mode.lower() == "step" or mode.lower() == "stepm" or mode.lower() == "stepc":
            print( "Position of STEP : %s" % xpeak)
            print( "Position of STEPM: %s" % xcms)
            print( "Position of STEPC: %s" % xcen)
        # --- Step-like signals
        if mode.lower() == "slit" or mode.lower() == "slitm" or mode.lower() == "slitc":
            print( "Position of SLIT : %s" % xpeak)
            print( "Position of SLITM: %s" % xcms)
            print( "Position of SLITC: %s" % xcen)
        print( "Chi^2 value of Gaussian fit: %.7f" % chi_2)

    # --- Assign the correct value to the goal motor position
    if mode.lower() == "peak" or mode.lower() == "dip" or mode.lower() == "step" or mode.lower() == "slit":
        xpos = xpeak
    elif mode.lower() == "cms" or mode.lower() == "dipm" or mode.lower() == "stepm" or mode.lower() == "slitm":
        xpos = xcms
    elif mode.lower() == "cen" or mode.lower() == "dipc" or mode.lower() == "stepc" or mode.lower() == "slitc":
        xpos = xcen

    # --- Last check if xpos is within scanning range
    if xpos < np.amin(x) or xpos > np.amax(x):
        xpos  = np.mean(x)
        xpeak = np.mean(x)
        xcms  = np.mean(x)
        xcen  = np.mean(x)
        message = 'Error %s: Goal position outside of scan range!' % mode.upper()
        return message, xpos, xpeak, xcen, xcms

    message = 'success'
    return message, xpos, xpeak, xcms, xcen
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _check4peak(x,y):
    debug  = 1
    # --- initialize output variables
    ispeak = False
    peaki  = int(round(len(x)/2))                # --- Dummy peak index (center point) 
    peakw  = 0.125 * (np.amax(x)-np.amin(x))     # --- Dummy peak width
    # --- Calculate smoothed derivative 'sdy' of intensity signal (of identical length!)
    SmoothWidth, SmoothType, Ends = (5, 3, 1)
    sdy = _fastsmooth( _deriv(y), SmoothWidth, SmoothType, Ends)
    if debug == 0:
        _plt.figure(102)
        xval = list( range(1,len(y)+1))
        _plt.plot(xval, _deriv(y), 'ro-')
        _plt.plot(xval, sdy     , 'bo-')
        _plt.show()
    # --- Prepare some variables
    L      = len(y)
    w      = int(SmoothWidth)
    if w % 2 == 0:
        hw = int(w/2)                  # --- halfwidth of even smoothing values
    else:
        hw = int(np.ceil(float(w)/2))  # --- halfwidth of odd smoothing values
    # --- Collect information of possible peaks
    peak = 1
    p0   = 0.0 * y                     # --- initialize p0 (peak number)
    p1   = 0.0 * y                     # --- initialize p1 (index of peak position)
    p2   = 0.0 * y                     # --- initialize p2 (index of nearest previous  maximum of sdy)
    p3   = 0.0 * y                     # --- initialize p3 (index of nearest following minimum of sdy)
    p4   = 0.0 * y                     # --- initialize p4 (difference value between maximum and minimum) 
    # --- Find zero crossings in the smoothed derivative 'sdy' (from positive to negative)
    for ind in range((hw-1),L-(hw-1)):
        # if float(np.sign(sdy[ind])) > float(np.sign(sdy[ind+1])):
        if sdy[ind] >= 0 and sdy[ind+1] < 0:
            kmax = ind
            while kmax > 0 and sdy[kmax-1] > sdy[kmax]:
                kmax = kmax -1
            kmin = ind+1
            while kmin < L-1 and sdy[kmin] > sdy[kmin+1]:
                kmin = kmin + 1
            p0[ind] = peak
            p1[ind] = ind
            p2[ind] = kmax
            p3[ind] = kmin
            p4[ind] = sdy[kmax] - sdy[kmin]
            peak    = peak + 1
    # --- Check the 'most promising' peak 
    # --- By using the index of the maximum of p4 (largest difference in sdy!)
    imax = np.argmax(p4)
    if p0[imax] > 0:           # --- Found (at least) one (positive to negative) zero crossing
        if max(p0) > 1:        # --- More than one possible peak
            if p3[imax] - p2[imax] >= w and p4[imax] >  3.0 * np.std(sdy):
                ispeak = True
                peaki  = int(p1[imax])
                peakw  = 1 / 2.355 * abs(x[int(p2[imax])] - x[int(p3[imax])])
        elif max(p0) == 1:     # --- Just one possible peak (relax the other conditions)
            if p3[imax] - p2[imax] >= w and p4[imax] >  1.0 * np.std(sdy):
                ispeak = True
                peaki  = int(p1[imax])
                peakw  = 1 / 2.355 * abs(x[int(p2[imax])] - x[int(p3[imax])])
    # --- Return output variables
    return ispeak, peaki, peakw
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _fastsmooth(y, SmoothWidth, SmoothType, Ends):
    debug = 0
    # --- check/control variable 'Ends' 
    Ends = int(Ends)
    if Ends <= 0:
        Ends = 0
    if Ends >= 1:
        Ends = 1
    # --- check/control variable 'SmoothType' 
    SmoothType = int(SmoothType)
    if SmoothType < 1:
        SmoothType = 1
    if SmoothType > 3:
        SmoothType = 3
    # --- check/control variable 'SmoothWidth' 
    SmoothWidth = int(SmoothWidth)
    if SmoothWidth < 2:
        SmoothWidth = 2
    # ---
    if debug == 1:
        print( "%s %s %s " % (repr( SmoothWidth), repr( SmoothType), repr( Ends)))
    # --- call the actual smoothing function
    if SmoothType == 1:
        sy = _smoothy(y , SmoothWidth, Ends)
    elif SmoothType == 2:
        y1 = _smoothy(y , SmoothWidth, Ends)
        sy = _smoothy(y1, SmoothWidth, Ends)
    elif SmoothType == 3:
        y1 = _smoothy(y , SmoothWidth, Ends)
        y2 = _smoothy(y1, SmoothWidth, Ends)
        sy = _smoothy(y2, SmoothWidth, Ends)

    if debug == 1:
        _plt.figure(101)
        xval = list( range(1,len(y)+1))
        _plt.plot(xval,  y, 'ro-')
        _plt.plot(xval, sy, 'bo-')
        if SmoothType >= 2:
            _plt.plot(xval, y1, 'k-')
        if SmoothType >= 3:
            _plt.plot(xval, y2, 'k-')
        _plt.show()

    return sy
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _smoothy(y, sw, ends):
    debug = 0
    # --- initialize sy (smoothed signal)
    sy    = 0.0 * y
    # --- check/control variable 'ends' 
    ends = int(ends)
    if ends <= 0:
        ends = 0
    if ends >= 1:
        ends = 1
    # --- check/control variable 'sw' (smoothing width)
    sw  = int(sw)
    if sw < 2:
        sw = 2
    # ---
    if debug == 1:
        print( "%s, %s" %  (str(sw), str(ends)))
    # --- check/control variable 'hw' (smoothing halfwidth)
    if sw % 2 == 0:  
        hw = int(sw/2)
    else:
        hw = int(np.ceil(float(sw)/2))
    # ---
    L  = len(y)                        # --- retrieve the number of y elements
    # --- smooth the center region of y
    SP = sum(y[0:sw-1])
    for ind in range(0,L-sw):
        sy[ind+hw-1] = SP
        SP           = SP - y[ind] + y[ind+sw]
    sy[L-hw] = sum(y[-sw:-1])
    sy = sy / sw
    # --- if required taper the ends
    if ends == 1:
        taperpoints = hw - 1
        sy[0] =0
        for ind in range(1,taperpoints):
            sy[ind]    = np.mean(y[0 : ind])
            sy[-ind-1] = np.mean(y[-ind-1:-1])
        sy[-1] =0
    return sy
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _deriv(y):
    dy     = 0.0 * y
    dy[0]  = y[ 1] - y[ 0]
    dy[-1] = y[-1] - y[-2]
    for ind in range(1,len(y)-1):
        dy[ind] = (y[ind+1] - y[ind-1]) / 2
    return dy
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _center_of_mass(x,y):
    # ---
    debug = 0
    if debug == 1:
        _plt.figure(103)
        _plt.plot(x, y, 'ro-')
        _plt.show()
    # ---
    ys = y * x / y.sum()
    cy = ys.sum()
    return cy
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _gauss(x, *p):
    offset, amplitude, center, sigma = p
    gau = offset + amplitude * np.exp(-(x-center)**2/(2.*sigma**2))
    return gau
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
def _chi2(npara, exp_data, sim_data):
    delta = (exp_data-sim_data)**2
    gam   = np.abs(sim_data)
    chi2  = delta.sum() / gam.sum()
    chi2  = chi2 / (len(exp_data)-npara)
    return chi2
# --------------------------------------------------------------------------- #

