#!/usr/bin/env python
"""
Install the python-pyspectra package on a host

./DoDebianInstall.py <hostName>

"""
import argparse, sys, os
import HasyUtils
import handleVersion

def main(): 

    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        usage='%(prog)s [options]', 
        description= "Install pyspectra debian package on some host")
    
    parser.add_argument( '--p2', dest="p2", action="store_true", help='select python2 package')
    parser.add_argument( '--p3', dest="p3", action="store_true", help='select python3 package')
    parser.add_argument( 'hostName', nargs=1, default='None', help='hostname where the package is to be installed')  
    args = parser.parse_args()

    if not args.p2 and not args.p3:
        print( "DoDebianInstall.py: select --p2 xor --p3")
        return 
    if args.p2 and args.p3:
        print( "DoDebianInstall.py: select --p2 xor --p3")
        return 
        
    if args.hostName == "None": 
        print( "DoDebianInstall.py: specify hostname")
        sys.exit( 255)

    if len( args.hostName) != 1: 
        print( "DoDebianInstall.py: specify ONE host")
        sys.exit( 255)
        
    host = args.hostName[0]

    print( ">>> DoDebianInstall.py %s" % (host))

    if not HasyUtils.checkHostOnline( host): 
        print( "DoDebinaInstall.py: %s is not online " % host)
        sys.exit( 255)

    if not HasyUtils.checkHostRootLogin( host): 
        print( "DoDebinaInstall.py: %s no root login " % host)
        sys.exit( 255)

    if args.p3: 
        argout = os.popen('ssh root@%s "dpkg --status python3-sardana 2> /dev/null || echo failed"' % host).read()
        argout = argout.strip()
        if argout.find( 'failed') != -1:
            print( "DoDebianInstall.py: python3-pyspectra does not match sardana version of %s" % host)
            return 
    else: 
        argout = os.popen('ssh root@%s "dpkg --status python-sardana 2> /dev/null || echo failed"' % host).read()
        argout = argout.strip()
        if argout.find( 'failed') != -1:
            print( "DoDebianInstall.py: python-pyspectra (python2) does not match sardana version of %s" % host)
            return 

    version = handleVersion.findVersion()

    argout = os.popen('ssh root@%s "uname -v"' % host).read()
    argout = argout.strip()

    if argout.find( 'Debian') == -1: 
        print( "DoDebinaInstall.py: %s does not run Debian " % host)
        sys.exit( 255)

    if args.p3:
        debName = "python3-pyspectra_%s_all.deb" % version
    else: 
        debName = "python-pyspectra_%s_all.deb" % version
    #
    # copy the package to the install host
    #
    if os.system( "scp ./DebianPackages/%s root@%s:/tmp" % (debName, host)):
        print( "trouble copying the package to %s" % host)
        sys.exit( 255)
    #
    # remove the existing package, may not exist on the host
    #
    if os.system( 'ssh -l root %s "dpkg -r python-pyspectra"' % host): 
        pass
    if os.system( 'ssh -l root %s "dpkg -r python3-pyspectra"' % host): 
        pass
    #
    # install the new package
    #
    if os.system( 'ssh -l root %s "dpkg -i /tmp/%s"' % ( host, debName)): 
        print( "trouble installing the package on %s" % host)
        sys.exit( 255)
    #
    # delete the deb file
    #
    if os.system( 'ssh -l root %s "/bin/rm /tmp/%s"' % (host, debName)):
        print( "trouble removing deb file on %s" % host)
        sys.exit( 255)

    print( ">>> DoDebianInstall.py %s DONE" % host)
    return 

if __name__ == "__main__": 
    main()
