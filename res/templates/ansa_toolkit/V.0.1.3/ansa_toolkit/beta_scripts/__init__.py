#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import re
import string
		
#===============================================================================

DEFAULT_BUTTON_GROUP = 'Auxiliary'
TOOL_PREFIX = '*.bs'
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
# BUTTON_PATTERN = re.compile(r'defbutton\s+(\w*)\s*\(\s*\w*\s*\)(\w*)')
BUTTON_PATTERN = re.compile(r'defbutton\s+(\w*)\s*\(\s*(\w*)\s*\)\s*(\w*)\s*(\{?)')

sys.path.append(PATH_SELF)

#===============================================================================

betaModules = dict()
for filename in glob.glob(os.path.join(PATH_SELF, TOOL_PREFIX)):
	moduleName = os.path.basename(os.path.splitext(filename)[0])
	bsPath = os.path.join(PATH_SELF, moduleName + '.bs') 
	
# 	print('Analysing:', moduleName)
	try:
		fi = open(bsPath, 'rt')
		executable = None
		group = None
		for line in fi.readlines():
			line = line.strip()
			match = re.match(BUTTON_PATTERN, line)
			if match:
				executable = match.group(1)
				fcnArgument = match.group(2)
				group = match.group(3)
				bracket = match.group(4)
				if len(group) < 2:
					group = DEFAULT_BUTTON_GROUP
				break
		fi.close()
		if executable is not None:
			betaModules[moduleName] = {
				'executable' : executable, 'group' : group}
	except Exception as e:
		pass
# 		print('Failed to analyse module')
# 		print(str(e))

#===============================================================================

def getModuleContent(moduleName):
	
	bsPath = os.path.join(PATH_SELF, moduleName + '.bs') 
	outputName = os.path.join(PATH_SELF, 'tools','tool_%s.bs' % moduleName)
	
	fi = open(bsPath, 'rt')
	output = open(outputName, 'wt')
	for line in fi.readlines():
		#line = line.strip()
		match = re.match(BUTTON_PATTERN, line)
		if match:
			executable = match.group(1)
			group = match.group(3)
# 			line = 'def %s()' % match.group(1)
			line = line.replace('defbutton', 'def')

# 		output.write('%s\n' % line)
		output.write(line)
	output.close()
	fi.close()
	
	return executable, group, outputName


#===============================================================================

HEADER = '''
import os
import sys

import ansa
from ansa import betascript

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

sys.path.append(PATH_SELF)
import beta_scripts

#===============================================================================
# load *.bsx modules
@ansa.session.defbutton('SKODA', 'Element Size')
def callBetaScriptModule_CheckElementSize():
    betascript.LoadExecuteFunc(
        os.path.join(PATH_SELF, 'Check_element_size1314.bsx'), 'CheckElementSize')

@ansa.session.defbutton('SKODA', 'Midsurface')
def callBetaScriptModule_Midsurface():
    betascript.LoadExecuteFunc(
        os.path.join(PATH_SELF, 'SKODA_SkinExtraction.bsx'), 'MIDSURFACE')

#===============================================================================

@ansa.session.defbutton('CHECKs', 'model_check')
def callBetaScriptModule_model_check():
    moduleModelCheck = betascript.LoadModule(os.path.join(PATH_SELF, 'model_check', 'model_check.bs'))
    betascript.ExecuteFunc(moduleModelCheck, 'model_check')

#===============================================================================


'''

CALL_MODULE = '''\n@ansa.session.defbutton('${group}', '${executable}')
def callBetaScriptModule_${moduleName}():
    betascript.LoadExecuteFunc(
        os.path.join(PATH_SELF,'${moduleName}.bs') , '${executable}')
'''

content = HEADER

for moduleName in betaModules:
	
	executable = betaModules[moduleName]['executable']
	group = betaModules[moduleName]['group']
	
	newString = string.Template(CALL_MODULE)
	content += newString.safe_substitute(
		{'group': group, 'executable':executable, 'moduleName':moduleName}) 


fo = open(os.path.join(PATH_SELF, 'create_buttons.py'), 'wt')
fo.write(content)
fo.close()

import create_buttons
