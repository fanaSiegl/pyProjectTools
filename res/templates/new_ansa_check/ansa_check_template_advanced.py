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
else:
	PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

# ==============================================================================

class DummyEntityCheckItem(check_base_items.BaseEntityCheckItem):
	
	''' This class should be modified according to the desired ANSA check functionality.
	
	Add your own check methods and their fix functions (if any) and modify checkEntity() method in order to perform the check.
	All IssueDefinition instances should be registered using register() method in order to add them into appropriate ANSA check reports.
	
	The minimum implementation of the subclass in order to be compatible with the "safeRun" decorator and the "checkDescription":
		
		class DummyEntityCheckItem(check_base_items.BaseEntityCheckItem):
			SOLVER_TYPE = constants.ABAQUS
			ENTITY_TYPES = ['SHELL']
			AUTHOR = 'firstName LastName, <email@idiada.cz>'
		
		
		"'''
	
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['SHELL']
	AUTHOR = 'firstName LastName, <email@idiada.cz>'
	
	reportNames = ['Dummy check name 1', 'Dummy check name 2']
	
	#-------------------------------------------------------------------------
	
	def checkEntity(self):
		
		''' All checks to be performed are supposed to be called here and reported issues are supposed
		to be registered '''
		
		issues = list()
		
		# run all checks and update the list of issues
		issues.extend(self.dummyCheckOne())
		issues.extend(self.dummyCheckTwo())
		
		# register issues to the report
		self.registerIssues(issues)
			
	#-------------------------------------------------------------------------
	
	def dummyCheckOne(self):
		
		''' This is supposed to return a list of IssueDefinition instances or an emplty list
		if there are no issues detected. 
		
		IssueDefinition class (imported from external "check_base_items" module):
		
		class IssueDefinition(object):
			def __init__(self, reportName, entities, status, description, hasFix=False, fixFcnName='', fixValue=''):
				
				...
		'''
		
		issueDefinitions = list()
				
		# check entity - creating a new IssueDefinition instance
		if self._attributes['Name'] != 'Dummy element name':
			issue = check_base_items.IssueDefinition(
				'Dummy check name 1', [self.entity], 'error', 'This is dummy check description.',
				True, 'fixDummyIssueOne', 'Dummy element name')
			issueDefinitions.append(issue)
		
		# ANSA check parameters from the dialog if defined in the "checkDescription"
		# can be accessed in "self.params: attribute
		print('Input parameters:', self.params)
		
		return issueDefinitions
		
	#-------------------------------------------------------------------------
	@classmethod
	def fixDummyIssueOne(cls, issue):
		
		''' This is fix function for "dummyIssueOne" check. 
		
		Fix function tries to fix the issue with the given fixValue in the first step
		and re-uses the parent check function to re-check that everything is ok.. '''
		
		entities = issue.entities
		fixValue = issue._fixFcnValue
		
		# fix entites
		for entity in entities:
			print('Fixing entity:', entity)
			entity.set_entity_values(cls.SOLVER_TYPE, {'Name' : fixValue})
		
		# re-check entities for issues
		persistingIssues = list()
		for entity in entities:
			checkItem = DummyEntityCheckItem(entity)
			newIssues = checkItem.dummyCheckOne()
			persistingIssues.extend(newIssues)
		
		# set new issue status if everything is ok
		if len(persistingIssues) == 0:
			print('Entity %s fixed.' % entity)
			
			issue.status = 'ok'
			issue.is_fixed = True
			
	#-------------------------------------------------------------------------
	
	def dummyCheckTwo(self):

		''' This is supposed to return a list of IssueDefinition instances or an emplty list
		if there are no issues detected. '''
		
		return []

# ==============================================================================
@check_base_items.safeExecute(DummyEntityCheckItem, 'An error occured during the check procedure!')
def checkFunctionName(entities, params):
			
	# check given entities
	for entity in entities:
		checkItem = DummyEntityCheckItem(entity, params)
		checkItem.checkEntity()
			
	return DummyEntityCheckItem.getReports()

# ==============================================================================
@check_base_items.safeExecute(DummyEntityCheckItem,  'An error occured during the fix procedure!')
def fixFunctionName(issues):
	
	# run fix functions if possible
	for issue in issues: 
		if issue.has_fix:
			DummyEntityCheckItem.fixIssue(issue)

# ==============================================================================

def _debugModeTestFunction(debugedCheckItem):
	
	''' This function is executed if the DEBUG module attribute is set to 1 (True) and its purpose is to check whether the new ANSA check
	and its fix function definted in the corresponding DummyEntityCheckItem class work as expected. If there is an issue found and a fix
	function  available, fix function is executed automatically. '''
	
	
	# select test entities
	entities = base.PickEntities(debugedCheckItem.SOLVER_TYPE, debugedCheckItem.ENTITY_TYPES)
	
	# check "checkDescription" definition
	print('Checking "checkDescription" definition')
	checkFunction = getattr(sys.modules[__name__], checkOptions['exec_action'][0])	
	fixfunction = getattr(sys.modules[__name__], checkOptions['fix_action'][0])
	print('\tCheck function found:', checkFunction)
	print('\tFix function found:', fixfunction)
	
	# check selected entities
	checkReportTables = checkFunction(entities, [])
	
	# check found issues
	for checkReportTable in checkReportTables:
		print('Report:', checkReportTable.description)
		for issue in checkReportTable.issues: 
			print('\t', issue.status, issue.description)
			if issue.has_fix:
				print('\tIs going to be fixed...')
					
	# try to fix issues automatically if possible
	fixfunction(debugedCheckItem.getIssues())
	
# ============== this "checkDescription" is crucial for loading this check into ANSA! =========================

# update this dictionary in order to load this check automatically!
checkOptions = { 'name': '$ansaCheckName', 
	'exec_action': ('checkFunctionName', os.path.realpath(__file__)), 
	'fix_action':  ('fixFunctionName', os.path.realpath(__file__)), 
	'deck': DummyEntityCheckItem.SOLVER_TYPE, 
	'requested_types': DummyEntityCheckItem.ENTITY_TYPES, 
	'info': 'Check BEAM Elements'}

# do not modify this line! "checkDescription" must exist in order to load this check automatically!
checkDescription = base.CheckDescription(**checkOptions)

# add ANSA check attribute definition (string, integer or boolean)
checkDescription.add_str_param('name', 'value')
# checkDescription.add_int_param('name', 1)
# checkDescription.add_bool_param('name', True)

# ==============================================================================
	
if __name__ == '__main__' and DEBUG:
	
	_debugModeTestFunction(DummyEntityCheckItem)
		
# ==============================================================================

