#!/usr/bin/env python
# this scipt is executed with 
#
#   $ cd /home/kracht/Misc/pySpectra
#   $ python setup.py sdist
#     to build the source distribution, 
#     creates dist/python-hasyutils-1.0.tar.gz 
#     the tarball is used for remote installation only
#
#   root$ python setup.py install
#   root$ python setup.py clean
#
# to make a debian package ( or e.g. 'DoDebianBuild.pl haso113u' and 'DoDebianInstall.pl hastodt'): 
# 
# scp dist/python-pyspectra-1.0.tar.gz haso113u:/home/kracht/Misc/DebianBuilds
#   we assume that the directory 
#     haso113u:/home/kracht/Misc/DebianBuilds/python-pyspectra-1.0
#   does not exist
#
# ssh haso113u cd /home/kracht/Misc/DebianBuilds && /bin/rm -rf python-pyspectra-1.0
# ssh haso113u "cd /home/kracht/Misc/DebianBuilds && tar xvzf python-pyspectra-1.0.tar.gz"
# ssh haso113u "cd /home/kracht/Misc/DebianBuilds && mv python-pyspectra-1.0.tar.gz python-pyspectra_1.0.orig.tar.gz"
#
#   haso113u$ cd python-pyspectra-1.0/
#   haso113u$ dh_make --native -s -y
#     answer question 'Type of package' with 's' 
#
#    then change debian/control:
#     Source: python-pyspectra
#     X-Python-Version: >= 2.7
#     Section: unknown
#     Priority: extra
#     Maintainer: Thorsten Kracht <thorsten.kracht@desy.de>
#     Build-Depends: python-all, debhelper (>= 8.0.0)
#     ... 
#
#   haso113u$ debuild -us -uc
#
#   haso113u$ cd ..
#   haso113u$ scp python-pyspectra_1.0_amd64.deb hastodt:/tmp
#
#   root@hastodt# dpkg -r python-pyspectra                      # to remove the package
#   root@hastodt# dpkg -i /tmp/python-pyspectra_1.0_amd64.deb   # to install the package
#
#   dpkg --list | grep -i python-hasy
#     list installed packages
#
from distutils.core import setup, Extension
import sys, os, commands

version = commands.getoutput( './findVersion.pl')
version = version.strip()


setup( name="python-pyspectra", 
       version=version,
       author = "Thorsten Kracht",
       author_email = "thorsten.kracht@desy.de",
       url = "https://github.com/thorstenkracht/PySpectra",    
       #
       # beware: MANIFEST somehow memorizes the script names (can be deleted)
       #
       scripts = [ 'PySpectra/pyspViewer.py',
                   'PySpectra/sardanaMonitor/pyspSM.py',
                   ],
       packages = ['PySpectra', 
                   'PySpectra/dMgt', 
                   'PySpectra/ipython', 
                   'PySpectra/mtpltlb', 
                   'PySpectra/pqtgrph']
   )
