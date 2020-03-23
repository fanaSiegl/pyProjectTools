# PYTHON script
# -*- coding: utf-8 -*-

'''
Project name
============

Project function description.

* does requires something
* does something
* creates something as an output

Location
--------

toolbarName>buttonName

Usage
-----

* click here
* click there
* click there

Requirements
------------

.. warning::
    
    Requires something
    
* designed for META V.19.1.1

'''

#=========================== to be modified ===================================

TOOLBAR_NAME = 'toolbarName'
DOCUMENTATON_GROUP = 'META tools'
DOCUMENTATON_DESCRIPTION = 'Python application one line description.'

#==============================================================================

import os
import sys
from traceback import format_exc

import meta
from meta import base, guitk

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

meta.ImportCode(os.path.join(PATH_SELF, 'domain', 'util.py'))

#==============================================================================

class Project(object):

	APPLICATION_NAME = 'New project name'

	def __init__(self):

		self.method1()

	#--------------------------------------------------------------------------

	def method1(self):

		showInfoMessage('%s\n%s' % (self.APPLICATION_NAME, util.getVersionInfo()))


# ==============================================================================

def showCriticalMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxCritical, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)

# ==============================================================================

def showInfoMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxInformation, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)
	
#==============================================================================

def main():

	main.__doc__ = __doc__

	try:
		project = Project()
	except Exception as e:
		print(format_exc())
		showCriticalMessage(str(e))

#==============================================================================

if __name__ == '__main__':
	main()
