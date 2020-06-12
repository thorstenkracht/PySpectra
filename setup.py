#!/usr/bin/env python

from distutils.core import setup
import handleVersion

version = handleVersion.findVersion()

setup( name="python-pyspectra", 
       version=version,
       author = "Thorsten Kracht",
       author_email = "thorsten.kracht@desy.de",
       url = "https://github.com/thorstenkracht/PySpectra",    
       scripts = [ 'PySpectra/bin/pyspViewer.py',
                   'PySpectra/bin/pyspMonitor.py'],
       packages = ['PySpectra', 
                   'PySpectra/examples', 
                   'PySpectra/ipython', 
                   'PySpectra/mtpltlb', 
                   'PySpectra/pqtgrph']
   )
