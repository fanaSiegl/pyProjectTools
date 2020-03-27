# PYTHON script

import os
import sys
import glob
import configparser

import ansa
from ansa import base
from ansa import constants

# ==============================================================================

DEBUG = 0

# ==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'domain', 'util.py'))

# ==============================================================================

CHECK_PATTERN = 'check_*.py'
CHECKS_DOC_RST = 'checksDocString.rst'
PLIST_NAME = 'ANSA_UserDefined.plist'

# ==============================================================================

def loadChecks():
		
	checkDescriptions = list()
	documentedModules = list()
	for modulePath in glob.glob(os.path.join(util.getPathChecks(), CHECK_PATTERN)):

		moduleName = os.path.splitext(os.path.basename(modulePath))[0]
		ansa.ImportCode(modulePath)

		currentModule = globals()[moduleName]
		try:
			print('Loading: %s.' % currentModule.checkOptions['name'])
		except AttributeError as e:
			print('No checkDescription object found in: %s' % modulePath)
			continue

		if currentModule.__doc__ is not None:
			checkDocString = currentModule.__doc__
			documentedModules.append(moduleName)

			saveModuleDoc(moduleName, checkDocString)

		checkDescription = currentModule.checkDescription
		checkDescriptions.append(checkDescription)

	is_saved = base.CheckDescription.save(checkDescriptions, os.path.join(
		util.getPlistPath(), PLIST_NAME))
	print('%s checks loaded.' % is_saved)

	saveGeneralDoc(documentedModules)


# ==============================================================================

def saveGeneralDoc(documentedModules):

	content = '''.. toctree::
    :maxdepth: 1

'''

	for documentedModule in sorted(documentedModules, key=lambda n: n.replace('check_', '')):
		content += '    %s.rst\n' % documentedModule
		
	if DEBUG:
		print(content)
		return
	fo = open(
		os.path.join(util.getPathChecks(), 'doc', 'sphinx', 'source', CHECKS_DOC_RST), 'wt')
	fo.write(content)
	fo.close()

# ==============================================================================

def saveModuleDoc(moduleName, docString):
	
	if DEBUG:
		print(moduleName)
		print(docString)
		return
	fo = open(
		os.path.join(util.getPathChecks(), 'doc', 'sphinx', 'source', '%s.rst' % moduleName), 'wt')
	fo.write(docString)
	fo.close()

# ==============================================================================

if __name__ == '__main__':
	loadChecks()
