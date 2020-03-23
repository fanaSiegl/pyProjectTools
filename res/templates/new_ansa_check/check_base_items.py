# PYTHON script

'''
check_base_items
================

* contains common classes and functions for ansa checks.
* is supposed to be imported by other checks

'''

import os
import sys
from traceback import format_exc

import ansa
from ansa import base, constants, guitk


# ==============================================================================

DEBUG  = 0

# ==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

# ==============================================================================

class IssueDefinition(object):
	
	def __init__(self, reportName, entities, status, description, hasFix=False, fixFcnName='', fixValue=''):
		
		self.reportName = reportName
				
		self.attributes = {
			'entities' : entities, 'status' : status, 'description' : description, 'has_fix' : hasFix, '_fixFcnName' : fixFcnName, '_fixFcnValue' : fixValue}
		

# ==============================================================================

class BaseEntityCheckItem(object):
	
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['SHELL']
	AUTHOR = 'firstName LastName, <email@idiada.cz>'
	
	reportNames = ['Dummy check name 1', 'Dummy check name 2']
	reports = dict()
	
	def __init__(self, entity, params=[]):
		
		self.entity = entity
		self.params = params
		
		self._attributes = self.entity.get_entity_values(self.SOLVER_TYPE, self.entity.card_fields(self.SOLVER_TYPE))
		
		# initiate reports
		if len(self.reportNames) > 0 and len(self.reports.values()) == 0:
			BaseEntityCheckItem.createReports()
			
	#-------------------------------------------------------------------------
	@classmethod
	def createReports(cls):
		
		''' At the begining, report tables (groups for issues) are created '''

		for reportName in cls.reportNames:
			cls.reports[reportName] = base.CheckReport(type = reportName)
	
	#-------------------------------------------------------------------------
	@classmethod
	def getReports(cls):
		
		return [report for report in cls.reports.values()]
	
	#-------------------------------------------------------------------------
	@classmethod
	def getIssues(cls):
		
		issues = list()
		for report in cls.reports.values():
			issues.extend(report.issues)
		
		return issues

	#-------------------------------------------------------------------------
	@classmethod
	def fixIssue(cls, issue):
		
		# locate appropriate fix function according to the particular issue
		fixFcn = getattr(cls, issue._fixFcnName)
		fixFcn(issue)
		
		issue.update()
	
	#-------------------------------------------------------------------------
	
	def registerIssues(self, issueDefinitions):
		
		for issueDefinition in issueDefinitions:
			self.reports[issueDefinition.reportName].add_issue(**issueDefinition.attributes)
	
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
		if there are no issues detected. '''
		
		issueDefinitions = list()
		
		# check entity
		if self._attributes['Name'] != 'Dummy element name':
			issue = IssueDefinition(
				'Dummy check name 1', [self.entity], 'error', 'This is dummy check description.',
				True, '_fixDummyIssueOne', 'Dummy element name')
			issueDefinitions.append(issue)
		
		return issueDefinitions
		
	#-------------------------------------------------------------------------
	@classmethod
	def _fixDummyIssueOne(cls, issue):
		
		entities = issue.entities
		fixValue = issue._fixFcnValue
		
		# fix entites
		for entity in entities:
			print('Fixing entity:', entity)
			entity.set_entity_values(cls.SOLVER_TYPE, {'Name' : fixValue})
		
		# re-check entities for issues
		persistingIssues = list()
		for entity in entities:
			checkItem = BaseEntityCheckItem(entity)
			newIssues = checkItem.dummyCheckOne()
			persistingIssues.extend(newIssues)
		
		# set new issue status if everything is ok
		if len(persistingIssues) == 0:
			issue.status = 'ok'
	
	#-------------------------------------------------------------------------
	
	def dummyCheckTwo(self):

		''' This is supposed to return a list of IssueDefinition instances or an emplty list
		if there are no issues detected. '''
		
		return []

# ==============================================================================

def showErrorMessage(message):
	
	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxCritical, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)

# ==============================================================================

def showInfoMessage(message):
	
	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxInformation, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)

# ==============================================================================

def safeExecute(entityCheckItem=None, message=''):
	
	def baseWrap(fcn):
		def wrappedFcn(*args, **kwargs):
			try:
				ret = fcn(*args, **kwargs)
			except Exception as e:
				ret = []
				details = format_exc()
#				print(details)
				
				if entityCheckItem is not None and hasattr(entityCheckItem, 'AUTHOR'):
					author = entityCheckItem.AUTHOR
				else:
					author = 'N/A, <frantisek.siegl@idiada.cz>'

				# Prepare error message
				msg = message + ' Please report Traceback to:\n' +\
					author + '\n\n' + details

				# Create issue in Checks Manager
				err = base.CheckReport('Python errors')
				err.add_issue('error', [], msg)
				ret = [err]
			
			return ret
		return wrappedFcn
	return baseWrap

# ==============================================================================
@safeExecute(BaseEntityCheckItem, 'An error occured during the check procedure!')
def checkFunction(entities, params=[]):
			
		# check given entities
		for entity in entities:
			checkItem = BaseEntityCheckItem(entity)
			checkItem.checkEntity()
				
		return BaseEntityCheckItem.getReports()			

# ==============================================================================
@safeExecute(BaseEntityCheckItem,  'An error occured during the fix procedure!')
def fixFunction(issues):
	
	for issue in BaseEntityCheckItem.getIssues(): 
		if issue.has_fix:
			BaseEntityCheckItem.fixIssue(issue)

# ==============================================================================

def debugModeTestFunction(debugedCheckItem, testParams=dict()):
	
	''' This function is executed if the DEBUG module attribute is set to 1 (True) and its purpose is to check whether the new ANSA check
	and its fix function definted in the corresponding ItemChecker class work as expected. If there is an issue found and a fix
	function  available, fix function is executed automatically. '''
	
	print('Running ANSA check debug mode..')
	
	# select test entities
	showInfoMessage('Select entity to be checked.')
	entities = base.PickEntities(debugedCheckItem.SOLVER_TYPE, debugedCheckItem.ENTITY_TYPES)
	
	# check "checkDescription" definition
	print('Checking "checkDescription" definition')
	try:
		checkDescription = getattr(sys.modules['__main__'], 'checkDescription')
		checkFunction = getattr(sys.modules['__main__'], checkDescription.exec_action[0])
		fixfunction = getattr(sys.modules['__main__'], checkDescription.fix_action[0])

		print('\tCheck function found:', checkFunction)
		print('\tFix function found:', fixfunction)

	except AttributeError as e:
		print('Wrong check or fix function definition!', str(e))
		return
	
	# check selected entities
	checkReportTables = checkFunction(entities, testParams)
	
	# check found issues
	for checkReportTable in checkReportTables:
		print('Report:', checkReportTable.description)
		for issue in checkReportTable.issues: 
			print('\t', issue.status, issue.description)
			if issue.has_fix:
				print('\tIs going to be fixed...')
					
	# try to fix issues automatically if possible
	issues = list()
	for report in checkReportTables:
		issues.extend(report.issues)
	
	print('Trying fix function..')
	fixfunction(issues)
			
# ==============================================================================
	
if __name__ == '__main__' and DEBUG:
	debugModeTestFunction(BaseEntityCheckItem)
	
# ==============================================================================