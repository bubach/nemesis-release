#
# intfbuilder.py
#
# Copyright 1998 Dickon Reed
#

# intfbuilder is a tool to build a set of interfaces. It is invoked with the 
# name of a directory in which is to work. Unlike make, intfbuilder maintains a
# cache (name set by the value of cachefilename). If the cache is missing (ie
# the first time interface builder is executed, or if the user has blown it
# away) then no assumptions are made, and every file is regenerated. If 
# intfbuilder exists, it contains the mtimes of every interface believed to
# have been generated, and the dependencies between interfaces and product
# files. It will decide which interface products need to be generated, 
# then generate the products by invoking various tools. It reads dependencies
# files generated by these tools, and then removes the files so that the
# dependency data is stored in one place.

# --selah--

# All this is horribly Nemesis/cl/astgen specific. I wrote it because it
# was too hard to get make to do this properly. It is really just a driver
# program for cl and astgen. 



# set this to one to build all interface ast files in one foul (sic) sweep
# This is usually a good move, but I leave the (untested) option of setting
# this to zero in case it screws up later or someone has to use an old version
# of cl that couldn't handle it
allatonce = 1
# configuration

cachefilename = 'intfbuilder.cache'
bigc = 'IntfTypes.c'

# set to true to blow away none-critical working files
tidyup = 1

from treeinfo import *
import os, sys, stat, posix, marshal, string, buildutils

def showcache(cache):
    i = cache.keys()
    i.sort()
    sys.stderr.write('(cache: '+`i`+')\n')


def isinterfacefilename(name):
    if name[-3:] == '.if':
	return 1

def writecache(name):
    sys.stderr.write('(Writing the cache')
    f = open(repo + '/' + cachefilename, 'w')
    marshal.dump(cache, f)
    f.close()
    sys.stderr.write(')\n')
    #howcache(cache)
    

def getbase(name):
    l = string.split(name , '.')
    if len(l) > 1:
	return l[0]

if not (len(sys.argv) in [2,3]):
    sys.stderr.write("""
Usage: python intfbuilder.py reponame [verbose]
""")
    sys.exit(1)

repo = build_tree_dir + '/' +sys.argv[1]
verbose = 0
if len(sys.argv) == 3 and sys.argv[2] == 'verbose':
    verbose = 1

os.chdir(repo)
repo = './'

files = os.listdir('.')

interfaces = filter(isinterfacefilename, files)

if verbose:
    sys.stderr.write('(there were '+`len(interfaces)`+' interfaces)\n')

######################################################################
# reload or create the cache

if cachefilename in files:
    sys.stderr.write('(Reading the cache)\n')
    f = open(repo + '/' + cachefilename, 'r')
    cache = marshal.load(f)
    f.close()
else:
    cache = {}
    sys.stderr.write('Warning; no cache found; creating one\n')

if verbose:
    showcache(cache)


######################################################################
# mark everything in the cache as dead

for interface in cache.keys():
    cache[interface]['live'] = 0

######################################################################
# update the cache, building a list of things that are out of date

nowoutofdate = {}

nonexistentstuff = []
changedstuff = []
newstuff = []
neverbuiltstuff = []

if verbose:
    sys.stderr.write('(Statting the interfaces)\n')

for interface in interfaces:
    interfacefile = repo + '/' + interface
    exists = 1
    try:
	statbuf = os.stat(interfacefile)
    except posix.error:
	exists = 0
    if not exists:
	nonexistentstuff.append(interface)
    else:
	mtime = statbuf[stat.ST_MTIME]
	if cache.has_key(interface):
	    if cache[interface].has_key('buildtime'):
		if cache[interface]['buildtime'] != mtime:
		    changedstuff.append(interface)
		    nowoutofdate[interface] = 'changed since last build'
	    else:
		neverbuiltstuff.append(interface)
		nowoutofdate[interface] = 'never succesfully built'
	else:
	    newstuff.append(interface)
	    nowoutofdate[interface] = 'new'
	    cache[interface] = { }
	cache[interface]['live'] = 1
	cache[interface]['mtime'] = mtime


if verbose:
    sys.stderr.write('(Analysis: interfaces that do not exist: '+`nonexistentstuff`+', interfaces that need rebuilding: '+`changedstuff`+', interfaces that are new: '+`newstuff`+', interfaces that have never been built: '+`neverbuiltstuff`+')\n')

######################################################################
# remove all the dead interfaces from the cache, blowing them away

murderer = 0

for interface in cache.keys():
    if cache[interface]['live']:
	# let it be
	pass
    else:
	sys.stderr.write('Destroying dead interface '+interface+'\n')
	basename = getbase(interface)
	# first remove all its files
	for file in files:
	    if file[0:len(basename+'.')] == basename+'.' and file[-3:] != '.if':
		try:
		    os.unlink(repo+'/'+file)
		except posix.error:
		    pass
		    
	# then toast it in the cache
	del cache[interface]
	murderer = 1

######################################################################
# check deps of the remaining interfaces to see if some of them are 
# now also out of date


flag = 1
while flag:
    flag = 0
    for interface in interfaces:
	if nowoutofdate.has_key(interface):
	    # don't loose sleep over interfaces that are already out of date
	    pass
	else:
	    if (not cache.has_key(interface)) or (not cache[interface].has_key('deps')):
		# we don't have deps for this; rebuild it to obtain deps
		nowoutofdate[interface] = 'to obtain deps'
		flag =  1
	    else:
		for dep in cache[interface]['deps']:
		    if nowoutofdate.has_key(dep):
			# rumbled! one of the deps has changed
			nowoutofdate[interface] = dep
			flag = 1
    
######################################################################
# show the user what has been decided

outofdate = nowoutofdate.keys()

outofdate.sort()
if verbose:
    for interface in outofdate:
	sys.stderr.write('(building '+interface+' reason: '+nowoutofdate[interface]+')\n')




######################################################################
# build the outofdate set

# pass 1; go through and build AST files for everything

failedcompiles = []


if allatonce and len(outofdate) > 0:
    compiled = 0
    try:
	print('HELLO MICHAEL I CAN SEE YOU cl -A -M '+string.join(outofdate, ' '))
	buildutils.system('cl -A -M '+string.join(outofdate, ' '), 0, verbose)
	compiled = 1
    except buildutils.NonZeroExitStatus:
	sys.stderr.write('Interfaces failed to compile\n')
	failedcompiles.append(outofdate)

for interface in outofdate:
    if not allatonce:
	compiled = 0
	try:
	    buildutils.system('cl -A -M '+interface, 0, verbose)
	    compiled = 1
	except buildutils.NonZeroExitStatus:
	    sys.stderr.write('Error; interface '+interface+' failed to compile\n')
	    failedcompiles.append(interface)



    if compiled:
	cache[interface]['buildtime'] = cache[interface]['mtime']
	basename = getbase(interface)

	depslist = []
	# code to slurp up the .d file
	o = open(basename+'.ast.d', 'r')
	contents = o.readline()
	o.close()
	deps = string.split(contents)
	for dep in deps[1:]:
	    depslist.append(dep[2:])

	cache[interface]['deps'] = depslist

if len(failedcompiles)>0:
    sys.stderr.write('Some interfaces failed to compile ('+`failedcompiles`+'); aborting\n')
    sys.stderr.write('Paranoid abort; all output of CL compiler assumed to be questionable\n')
    sys.exit(1)
    
# pass 2; rebuild the products of the AST files

if len(outofdate)>0:
    invocation = 'astgen P`pwd` ih def '

    for interface in outofdate:
	basename = getbase(interface)
	invocation = invocation + basename + '.ast '

    buildutils.system(invocation, 0, verbose)


######################################################################
# tidy up

files = os.listdir('.')
for file in files:
    rubbish = 0
    for extn in ['.ast.d']:
	if file[-len(extn):] == extn:
	    rubbish = 1
    #if file in ['IntfTypes.c', 'IntfTypes.o']:
	#rubbish = 1
    basename = getbase(file)
    if basename:
	interface = basename+'.if'
	# blow away any products of nonexistent interfaces
	if not cache.has_key(interface):
	    if file in [basename+'.def.c',
			basename + '.ast', basename + '.ih']:
		rubbish = 1
    if rubbish:
	#sys.stderr.write('Removing rubbish '+file+'\n')
	os.unlink(file)



######################################################################
# write the cache if is has changed, which only could have happened
# if we had outofdate files

if len(outofdate)>0 or murderer:
    writecache(cache)


######################################################################
# handle building IntfTypes.c

# iff it does not exist or we have just rebuilt some files

if (not 'IntfTypes' in files) or len(outofdate)>0 or murderer:
    if verbose: sys.stderr.write('(Generating '+bigc+')\n')
    bigcstr = """
/* this file autogenerated by IntfBuilder */

"""
    for interface in cache.keys():
	basename = getbase(interface)
	bigcstr = bigcstr + ('#include "'+basename+'.def.c"\n')

    bigcstr = bigcstr + """
const void *  const Types_primal[] = {
"""

    for interface in cache.keys():
	basename = getbase(interface)
	bigcstr = bigcstr + '\t&'+basename+'__intf,\n'
    
    bigcstr = bigcstr + """
\tNULL
};

/* END OF AUTOMATICALLY GENERATED FILED */
"""

    o = open(bigc, 'w')
    o.write(bigcstr)
    o.close()

    # now build it
    buildutils.system('gnumake IntfTypes', 0, 0)
else:
    if verbose: sys.stderr.write('(IntfTypes does not need rebuilding)\n')
