#! /usr/bin/env python

usage = """
checkoutandgo.py config_file_name

A tool for putting a bunch of files in a tree and executing a script on it.
It reads a config file. The config file defines a python dictionary. It should
start and end with curly braces. It must have attributes:

package: a list of (mode, package, path) tuples. See below.
basepath: the directory to extract the tree in to.

It may have the following extra attributes:

prcsrepo: the path of a PRCS repository
prcspath: the location of a PRCS binary
postfix: an extra postfix to stick on the end of basepath
actions: text of a shell script to execute in the new tree

The package attribute lists the packages to be checked out. The action
is determined by the mode attribute. The second memebr of the tuple is
an argument to the code for the specified mode, and the third is the path
within the new tree to place the code in. As a special case, if the path
is /.., then a package is extracted up one level. The modes are:

prcs: the argument should be a package name, then a colon, then a PRCS
      version ID

copy: the argument should be a path; the contents of the path will be copied
      recursively in to the tree

link: same as copy, except the contents are linked instead of copied


"""

import sys, os, tempfile, string, pwd, socket, time, pwd

def command(str):
    #sys.stderr.write('Command: '+str+'\n')
    return os.system(str)

def fatal(mesg):
    sys.stderr.write(mesg+'\n')
    sys.exit(1)

if len(sys.argv) != 2:
    fatal(usage)

if not os.path.exists(sys.argv[1]):
    fatal('Configuration file %s missing' % sys.argv[1])
    
o = open(sys.argv[1])
configfilecontents= o.read()
o.close()

globals = eval(configfilecontents)
if not globals.has_key('packages'):
    fatal('Missing packages entry in checkoutandgo configuration file')
if not globals.has_key('basepath'):
    fatal('Missing basepath entry in checkoutandgo configuration file')

packages = globals['packages']
basepath = globals['basepath']

basepath = string.replace(basepath, '$UID', pwd.getpwuid(os.getuid())[0])

if basepath[-1] == '/': basepath = basepath[:-1]

if len(basepath) < 2:
    fatal('basepath defined in configuration script is too short')
prcspath = globals.has_key('prcspath') and globals['prcspath'] or 'prcs'
prcsrepo = globals.has_key('prcsrepo') and globals['prcsrepo'] or None
actions = globals.has_key('actions') and globals['actions'] or ""
print 'Packages', packages
print 'Basepath', basepath

if not os.path.isdir(basepath):
    os.system('mkdir -p '+basepath)

command('(cd '+basepath+' && rm -rf *)')

mastertree = basepath + (globals.has_key('postfix') and ('/'+globals['postfix']) or '')
command('mkdir -p '+mastertree)

for (mode, package, destination) in packages:
    if destination[-3:] == '/..':
        destdir = mastertree + destination[:-3]
        spl = string.split(destdir, '/')
        destdirupone = string.join(spl[:-1], '/')
        destdir = destdirupone
    else:
        destdir = mastertree + destination
    
    os.system('mkdir -p '+destdir)

    #print 'Master tree is at %s, targetting %s, hitting %s' %(mastertree, destdir, destdirupone)
    # put some stuff in destdir
    if mode in [ 'copy', 'link']:
        # it is a directory full of stuff
        if mode == 'copy':
            print 'Copying '+package +' to '+destdir
            if command('cp -R '+package+'/* '+destdir):
                fatal('Copy of package '+package+' failed')
        else: # mode == 'link'
            if command('(cd '+destdir+' && lndir '+package+')'):
                fatal('lndir of package '+package+' failed')
    if mode == 'prcs':
        spl = string.split(package, ':')
        if len(spl)<2:
            fatal('Malformed prcs package name '+package+'; should be package:version')
        prcspackage = spl[0]
        prcsversionid = string.join(spl[1:], ':')

        # it is a PRCS package
        os.chdir(destdir)
        print prcspackage + ' in ' + destdir
        if command( (prcsrepo and ('PRCS_REPOSITORY='+prcsrepo+ ' ') or '')
                    + prcspath
                    +' checkout -f -r '+prcsversionid+' '+prcspackage):
            fatal('Checkout of package '+package+' failed')
            
o = open(mastertree+'/CONFIGURATION', 'w')
o.write(configfilecontents)
(uid,_,_,_,gcos,_,_) = pwd.getpwuid(os.getuid())
o.write('# generated by '+uid+'('+gcos+') on '+socket.gethostname()+' at '+time.ctime(time.time())+'\n')
o.close()

if actions != '':
    o = os.popen('/bin/sh', 'w')
    o.write('set -e\n')
    o.write('cd '+mastertree+'\n')
    o.write(actions)
    result =o.close()
    if not result in [None, 0]:
        fatal('ABORT: the configuration file actions script failed\n')


