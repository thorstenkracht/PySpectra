#!/usr/bin python

import os, sys

class handleVersion():
    def __init__( self, dirName = None):

        if dirName is None:
            raise ValueError( "handleVersion: missing dirName")

        self.dirName = dirName

        return

    def findVersion( self):
        """
        """
        try: 
            print( "findVersion: opening %s/versionTarBall.lis" % self.dirName)
            
            inp = open( "%s/versionTarBall.lis" % self.dirName, "r")
            for line in inp.readlines():
                if line.find( "#") != -1:
                    continue
                (major, minor) = line.split( ' ')[1].split( '.')
                break
        except Exception as e:
            print( "handleVersion.findVersion: caught an exception, dir: %s " % self.dirName)
            print( repr( e))
            sys.exit( 255)
        
        return "%s.%d" % ( int( major), int( minor))

    def incrementVersion( self):
        """
        """
        version = self.findVersion()

        (versionMajor, versionMinor) = version.split( '.')
        print( "incrementVersion: opening %s/versionTarBall.lis" % self.dirName)

        versionMinor = int( versionMinor) + 1

        try: 
            out = open( "%s/versionTarBall.lis" % self.dirName, "w")
            out.write( "#\n# do not edit this file\n#\n") 
            out.write( "version %d.%d\n" % ( int( versionMajor), int( versionMinor)))
            out.close()
        except Exception as e:
            print( "handleVersion.incrementVersion: caught an exception")
            print( repr( e))
            sys.exit( 255)
    
        return True
