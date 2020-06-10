#!/usr/bin/env python

from distutils.core import setup, Extension
import sys, os
import handleVersion

version = handleVersion.findVersion()


setup( name="python-pyspectra", 
       version=version,
       author = "Thorsten Kracht",
       author_email = "thorsten.kracht@desy.de",
       url = "https://github.com/thorstenkracht/PySpectra",    
       #
       # beware: MANIFEST somehow memorizes the script names (can be deleted)
       #
       scripts = [ 'PySpectra/pyspViewer.py',
                   'PySpectra/pyspMonitor.py',
                   ],
       packages = ['PySpectra', 
                   'PySpectra/examples', 
                   'PySpectra/ipython', 
                   'PySpectra/mtpltlb', 
                   'PySpectra/pqtgrph']
   )
