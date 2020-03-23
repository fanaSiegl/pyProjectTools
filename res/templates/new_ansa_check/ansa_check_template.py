# PYTHON script

'''
$ansaCheckName
===========================

Checks foo.

* searches all foo
* checks something

Usage
-----

**Primary solver** - ABAQUS

**Parameters**

* param1 - sets something
* param2 - sets something else

**Fix function**

* according to something fixes foo 1
* according to something fixes foo 2


'''

import os
import sys
from traceback import format_exc

import ansa
from ansa import base, constants, guitk

# ==============================================================================

# set DEBUG to 0 when the check is ready to be installed into ANSA with the pyProjectInstaller
DEBUG  = 1

# ==============================================================================

if DEBUG:
	PATH_SELF = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'
#	PATH_SELF = os.path.dirname(os.path.realpath(__file__))
else:
	PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

# ==============================================================================

class ItemChecker(check_base_items.BaseEntityCheckItem):
		
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['SHELL']
	AUTHOR = 'firstName LastName, <email@idiada.cz>'
	
# ==============================================================================
@check_base_items.safeExecute(ItemChecker, 'An error occured during the check procedure!')
def checkFunctionName(entities, params):
			
	checkReport = base.CheckReport(type = 'reportName')
	
	for entity in entities:
		# check entity
		attributes = entity.get_entity_values(ItemChecker.SOLVER_TYPE, entity.card_fields(ItemChecker.SOLVER_TYPE))
		
		if attributes['Name'] != 'Dummy element name':
			# add issue
			checkReport.add_issue(entities=[entity], status='error',
				description='issue description', has_fix=False)	
			
	return [checkReport]

# ==============================================================================
@check_base_items.safeExecute(ItemChecker,  'An error occured during the fix procedure!')
def fixFunctionName(issues):
	
	# run fix functions if possible
	for issue in issues: 
		if issue.has_fix:
			entities = issue.entities
	
# ============== this "checkDescription" is crucial for loading this check into ANSA! =========================

# update this dictionary in order to load this check automatically!
checkOptions = { 'name': '$ansaCheckName', 
	'exec_action': ('checkFunctionName', os.path.realpath(__file__)), 
	'fix_action':  ('fixFunctionName', os.path.realpath(__file__)), 
	'deck': ItemChecker.SOLVER_TYPE, 
	'requested_types': ItemChecker.ENTITY_TYPES, 
	'info': 'Check BEAM Elements'}

# do not modify this line! "checkDescription" must exist in order to load this check automatically!
checkDescription = base.CheckDescription(**checkOptions)

# add ANSA check attribute definition (string, integer or boolean)
checkDescription.add_str_param('name', 'value')
# checkDescription.add_int_param('name', 1)
# checkDescription.add_bool_param('name', True)

# ==============================================================================
	
if __name__ == '__main__' and DEBUG:
	
	testParams = {'name' : '6'}
	check_base_items.debugModeTestFunction(ItemChecker, testParams)
		
# ==============================================================================

