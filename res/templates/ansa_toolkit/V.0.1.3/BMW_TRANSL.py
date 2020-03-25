#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob

TOOLKIT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(TOOLKIT_PATH)

os.environ['ANSA_TOOLS'] = os.path.normpath(os.path.join(TOOLKIT_PATH, '..', '..', 'ansaTools'))
os.environ['TOOLKIT_PATH'] = TOOLKIT_PATH
os.environ['ANSA_IDIADA_PLUGINS'] = os.path.normpath(os.path.join(TOOLKIT_PATH, '..', '..', 'ansaTools', 'Plugins'))

import ansa_toolkit
import ansa
from ansa import base, constants

# ==============================================================================

CHECK_PATTERN = 'check_*.py'
PATH_CHECKS = os.path.normpath(os.path.join(TOOLKIT_PATH, '..', '..', 'ansaTools', 'checks', 'default'))

userChecksPath = os.path.join(TOOLKIT_PATH, 'checks', 'ANSA_UserDefined.plist')
templatePath = os.path.join(TOOLKIT_PATH, 'checks', 'IDIADA_BMW_Templates.plist')

# ==============================================================================

def loadChecks():

    checkDescriptions = list()
    documentedModules = list()
    for modulePath in glob.glob(os.path.join(PATH_CHECKS, CHECK_PATTERN)):
        
        moduleName = os.path.splitext(os.path.basename(modulePath))[0]
        ansa.ImportCode(modulePath)
        
        currentModule = globals()[moduleName]
        try:
            print('Loading: %s.' % currentModule.checkOptions['name'])
        except AttributeError as e:
            print('No checkDescription object found in: %s' % modulePath)
            continue    
                
        checkDescription = currentModule.checkDescription
        checkDescriptions.append(checkDescription)
    
    is_saved = base.CheckDescription.save(checkDescriptions, userChecksPath)
    print('%s checks loaded.' % is_saved)
    
# ==============================================================================

# update checks if necessary
if not os.path.exists(userChecksPath):
	loadChecks()

base.SetCurrentDeck(constants.ABAQUS)
base.SetANSAdefaultsValues({
    'Default_UserDefinedChecks_File' : userChecksPath,
    'Default_Templates_File' : templatePath
    })
