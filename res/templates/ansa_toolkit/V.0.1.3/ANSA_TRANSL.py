#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

# set base environment variables
if 'win' in sys.platform:
	ANSA_USER_CHECK_PLIST = 'ANSA_UserDefined_win.plist'
	
	os.environ['ANSA_TOOLS'] = r'\\mb-us2\fem\+software\SKRIPTY\tools\python\ansaTools'
	os.environ['TOOLKIT_PATH'] = r'\\mb-us2\fem\+software\SKRIPTY\tools\python\ansa_toolkit\default'
	os.environ['ANSA_IDIADA_PLUGINS'] = r'\\mb-us2\fem\+software\SKRIPTY\tools\python\ansaTools\Plugins'
	
else:
	ANSA_USER_CHECK_PLIST = 'ANSA_UserDefined.plist'
	PATH_SELF = os.path.dirname(os.path.realpath(__file__))
	PATH_TOOLS_PYTHON = os.path.normpath(os.path.join(PATH_SELF, '..', '..'))
	
	os.environ['ANSA_TOOLS'] = os.path.join(PATH_TOOLS_PYTHON, 'ansaTools')
	os.environ['TOOLKIT_PATH'] = os.path.join(PATH_TOOLS_PYTHON, 'ansa_toolkit', 'default')
	os.environ['ANSA_IDIADA_PLUGINS'] = os.path.join(PATH_TOOLS_PYTHON, 'ansaTools', 'Plugins')
	
sys.path.append(os.environ['TOOLKIT_PATH'])

import ansa_toolkit

from ansa import base, constants, mesh

userChecksPath = os.path.join(os.environ['ANSA_TOOLS'], 'checks', 'general_check', 'default', ANSA_USER_CHECK_PLIST)
templatePath = os.path.join(os.environ['TOOLKIT_PATH'], 'checks', 'IDIADA_Templates.plist')

#base.SetCurrentDeck(constants.ABAQUS)
base.SetANSAdefaultsValues({
	'Default_UserDefinedChecks_File' : userChecksPath,
	'Default_Templates_File' : templatePath
	})

# load defaults
#mesh.ReadMeshParams(os.path.join(os.environ['TOOLKIT_PATH'], '_bmw_defaults', '8_3mm_mixed.ansa_mpar'))
#mesh.ReadQualityCriteria(os.path.join(os.environ['TOOLKIT_PATH'], '_bmw_defaults', '8_3mm.ansa_qual'))