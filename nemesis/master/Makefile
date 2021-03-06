#########################################################################
#                                                                       #
#  Copyright 1994, University of Cambridge Computer Laboratory  	#
#                                                                       #
#  All Rights Reserved.						        #
#                                                                       #
#########################################################################
#
# DIRECTORY:
#
#	Root.
# 
# DESCRIPTION:
#
#	Toplevel Makefile
#
# ID : $Id: Makefile 1.5 Mon, 17 May 1999 18:37:22 +0100 dr10009 $
#

ROOT	= .

SUBDIRS	= glue mk repo h ntsc lib dev sys mod app boot doc links

CONFIG_SHELL=bash
ETAGS=etags

include $(ROOT)/mk/rules.mk

#
# Doing this in the build tree has several benefits.
# 1. Only get tags relevant to this architecture etc.
# 2. Can find tags in derived C and H files
TAGS: 	FRC
	rm -f TAGS
	find . -name *.[ch] | xargs $(ETAGS) --append 
	find . -name *.ih  | xargs $(ETAGS) --append 
	find . -name *.[S] | xargs $(ETAGS) --append --language asm
	cp TAGS $(SRCROOT)/TAGS

livedb.py: 	FRC
	rm -f livedb.py tags TAGS
	(command cd h && find . -name \*.h | xargs $(ETAGS) --append)
	mv h/TAGS TAGS
	cat glue/livedbstart > livedb.py
	PYTHONPATH=`pwd`/glue python glue/tagstodb.py TAGS  >> livedb.py
	PYTHONPATH=`pwd`/glue python glue/ifbuildercachetodb.py >> livedb.py
	cat glue/livedbend >> livedb.py

uses.txt: FRC
	@echo This is only useful if the tree has been built
	PYTHONPATH=`pwd`/glue python $(ROOT)/glue/depsshow.py > uses.txt

#
# simple interface to the build system
#

# #
# itso; do everything that can be done
#

itso:
	(cd glue && ./layfoundations.py +disable_locatetree +disable_gentreeinfo)

#
# replumb; force the tree to be replumbed. This updates the autoconf stuff
# and fixes up the interface directories.
#

replumb:
	-rm repocontents
	PYTHONPATH=$(ROOT)/glue python $(ROOT)/glue/plumbtree.py

#
# makefiles; build the makefiles
#

makefiles:
	PYTHONPATH=$(ROOT)/glue python -c "import geninfrastructure; geninfrastructure.go()"
	echo

#
# audit; show the status of all build items
#


audit:
	PYTHONPATH=$(ROOT)/glue python $(ROOT)/glue/audit.py compact


#
# gui; run the choices gui
#

gui:
	PYTHONPATH=$(ROOT)/glue python $(ROOT)/glue/choicesgui.py $(ROOT)/choices $(ROOT)/glue/packages/ccore.py


