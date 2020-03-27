#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import re

from domain import utils
from interfaces import githubio

#=============================================================================

INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_BASE']
DOCUMENTATON_PATH = INSTALL_PATHS['DOCUMENTATON_PATH']
DOC_RES = os.path.join(DOCUMENTATON_PATH, 'res')

SPHINX_SOURCE = os.path.join(DOC_RES, 'source')
SPHINX_DOCTREES = os.path.join(DOC_RES, 'build', 'doctrees')
SPHINX_HTML = os.path.join(DOC_RES, 'build', 'html')

#=============================================================================


class Tool(object):
    
    instances = list()
    
    VERSION_PATTERN = r'.*\*{1}\s+commit\s+(.*)\s+\({1}.*,\s+tag:\s+(V\.\d+\.\d+\.\d+).*'
    DOCUMENTATON_DESCRIPTION_LINE_NO = 2
    
    def __init__(self, parentGroup, name):
        
        self.parentGroup = parentGroup
        self.name = name
        self.path = os.path.join(self.parentGroup.path, self.name)
        
        self._txtContent = list()
#         self._version = ''
        self.versions = list()
        self._revisionHistoryFileName = os.path.join(self.path, 'revision_history.rst')
        self._txtFileName = os.path.join(self.path, self.name + '.txt')
        self._showExtendedInfo = False
        
        self._register(self)
        self._setupVersion()
        self._setupTxtContent()
        
    #---------------------------------------------------------------------------
    @classmethod
    def _register(cls, instance):
        
        cls.instances.append(instance)
                    
    #---------------------------------------------------------------------------
    
    def version(self):
        
        if len(self.versions) > 0:
            return self.versions[0]
        else:
            return 'N/A'
#         return self._version
    
    #---------------------------------------------------------------------------
    
    def getLocation(self):
        
        return self.parentGroup.parentLocation.name
    
    #---------------------------------------------------------------------------
    
    def _setupVersion(self):
        
        if os.path.isfile(self._revisionHistoryFileName):
            fi = open(self._revisionHistoryFileName, 'rt')
            lines = fi.readlines()
            fi.close()
            
            try:
                for line in lines:
                    match = re.match(self.VERSION_PATTERN, line)
                    if match:
                        self.versions.append(match.group(2))
#                         self._version = match.group(2)
#                         break
                    
            except Exception as e:
                print('Failed to obtain tool version of: %s' % self.name)
    
    #---------------------------------------------------------------------------
    
    def _setupTxtContent(self):
        
        if os.path.isfile(self._txtFileName):
            fi = open(self._txtFileName, 'rt')
            self._txtContent = fi.readlines()
            fi.close()
    
    #---------------------------------------------------------------------------
    
    def getToolTag(self):
        
        return '%s_%s' % (self.name, self.version())
    
    #---------------------------------------------------------------------------
    
    def isLocal(self):
        
        return self.parentGroup.isLocal() is True
    
    #---------------------------------------------------------------------------
    
    def showExtendedInfo(self, value):
        
        self._showExtendedInfo = value
    
    #---------------------------------------------------------------------------
    
    def toString(self):
        
        # fix location
        linkLine = self._txtContent[0]
        
        infoLine = self._txtContent[self.DOCUMENTATON_DESCRIPTION_LINE_NO]
        insertInfoIndex = infoLine.find('_ -') - 1
        prefix = infoLine[:insertInfoIndex]
        suffix = infoLine[insertInfoIndex:]
        
        versionInfo = ''
        if self._showExtendedInfo and not self.isLocal():
            versionInfo = ' (%s, remote %s)' % (self.version(), self.getLocation())
        elif self._showExtendedInfo and self.isLocal():
            versionInfo = ' (%s, %s)' % (self.version(), 'local')
        elif not self.isLocal():
            versionInfo = ' (remote %s)' % (self.getLocation())
        
        if len(versionInfo) > 0:
            self._txtContent[0] = linkLine.replace('_' + self.name, '_' + self.name + versionInfo)
            self._txtContent[self.DOCUMENTATON_DESCRIPTION_LINE_NO] = '%s%s%s' % (
                prefix, versionInfo, suffix)
            
        return ''.join(self._txtContent)
    
    #---------------------------------------------------------------------------
    
    def getOneLineDescription(self):
        
        description = self._txtContent[self.DOCUMENTATON_DESCRIPTION_LINE_NO]
        
        return '-'.join(description.split('-')[1:]).strip()
    

#=============================================================================

class ToolGroup(object):
    
    instances = list()
    tools = dict()
        
    def __init__(self, parentLocation, name):
        
        self.parentLocation = parentLocation
        self.name = name
        self.path = os.path.join(self.parentLocation.path, self.name)
        
        self._register(self)
        self.findTools()
        
    #---------------------------------------------------------------------------
    @classmethod
    def _register(cls, instance):
        
        cls.instances.append(instance)
        
        if instance.name not in cls.tools:
            cls.tools[instance.name] = dict()
    
    #---------------------------------------------------------------------------
    
    def findTools(self):
        
        for fileName in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, fileName)):
#                 self.tools[fileName] = Tool(self, fileName)
                
                currentTool = Tool(self, fileName)

                if currentTool.name not in self.tools[self.name]:
                    self.tools[self.name][currentTool.name] = list()
        
                self.tools[self.name][currentTool.name].append(currentTool)
    
    #---------------------------------------------------------------------------
    @classmethod
    def getListOfTools(cls, groupName):

        tools = list()
        for toolName in sorted(cls.tools[groupName].keys()):            
            toolItems = cls.tools[groupName][toolName]
            if len(toolItems) == 1:
                tools.append(toolItems[0])
            elif len(toolItems) > 1:
                
                # check if the version of the tool is the same
                versions = set()
                locations = list()
                for toolItem in toolItems:
                    versions.add(toolItem.version())
                    locations.append(toolItem.getLocation())
                # same version available locally
                if len(versions) == 1 and utils.getLocalLocation() in locations:
                    
                    for t in toolItems:
                        if t.isLocal():
                            tools.append(t)
                            break
                # same version available in remote locations
                elif len(versions) == 1:
                    tools.append(toolItems[0])
                # multiple versions at multiple locations
                elif len(versions) > 1:
                    tools.extend(toolItems)
                    for toolItem in toolItems:
                        toolItem.showExtendedInfo(True)
        
        return tools
    
    #---------------------------------------------------------------------------
    
    def isLocal(self):
        
        return self.parentLocation._isLocal is True
    
    #---------------------------------------------------------------------------
    

#=============================================================================

class ToolLocation(object):
    
    instances = dict()
    toolGroups = dict()
        
    def __init__(self, path):
        
        self.path = path
        self.name = os.path.basename(path)
        
        self._isLocal = False
        
        self._register(self)
        self.findToolGroups()
        
        if self.name == utils.getLocalLocation():
            self._isLocal = True
    
    #---------------------------------------------------------------------------
    @classmethod
    def _register(cls, instance):
        
        cls.instances[instance.name] = instance
    
    #---------------------------------------------------------------------------
    @classmethod
    def searchLocations(cls):
        
        ToolGroup.tools.clear()
        
        for location in utils.getListOfLocations():
            path = os.path.join(SPHINX_SOURCE, location)
            if os.path.isdir(path):
                cls(path)
    
    #---------------------------------------------------------------------------
    
    def findToolGroups(self):
                
        for fileName in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, fileName)):
                if fileName not in self.toolGroups: 
                    self.toolGroups[fileName] = list()
                self.toolGroups[fileName].append(ToolGroup(self, fileName))

    #---------------------------------------------------------------------------
    
    def isLocal(self):
        
        return self._isLocal is True
    
#=============================================================================

class ToolDocumentation(object):

    HEADER = '''IDIADA tools documentation
===========================

.. toctree::
   :maxdepth: 2

'''

    FOOTER = '''
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`'''
    
    SPHINX_SECTION_HIERARCHY = ['-', '^', '"']
    OUTPUT_NAME = 'index.rst'
        
    def __init__(self):
        
        self.indexContent = self.HEADER
        self.toolGroups = dict()
        
        self._initiateContent()
    
    #---------------------------------------------------------------------------
    
    def _initiateContent(self):
                
        ToolLocation.searchLocations()
        
        for groupName in sorted(ToolGroup.tools.keys()):            
                
            self.indexContent += self.getToolGroupString(groupName)
            
            tools = ToolGroup.getListOfTools(groupName)
            
            self.toolGroups[groupName] = tools
            for tool in tools:
                self.indexContent += tool.toString()
        
    #---------------------------------------------------------------------------
    
    def create(self):
        
        # create main index.rst file
        fo = open(os.path.join(SPHINX_SOURCE, self.OUTPUT_NAME), 'wt')
        fo.write(self.indexContent)
        fo.close()
        
        # create local documentation respecting sphinx environment 
        envExecutable = utils.getEnvironmentExecutable(utils.PATH_INI)
        if envExecutable is not None:
            os.system('%s -b html -d %s %s %s' % (
                os.path.join(os.path.dirname(envExecutable), 'sphinx-build'), 
                SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))
        else:
            os.system('/usr/bin/sphinx-build -b html -d %s %s %s' % (
                SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))
    
    #---------------------------------------------------------------------------
    
    def getToolGroupString(self, groupName):
    
        if '_' in groupName:
            groupName = groupName.replace('_',' ')
        
        string = '\n%s\n' % groupName
        string += '%s\n' % str(len(groupName)*self.SPHINX_SECTION_HIERARCHY[0])
        return string
    
    #---------------------------------------------------------------------------
    @classmethod
    def show(cls):
        
        os.system('%s %s &' % (
            utils.getDocumentationBrowser(),
            os.path.join(DOCUMENTATON_PATH, 'idiada_tools_doc.html')))
    
    #---------------------------------------------------------------------------
    @classmethod
    def initiateFromGithub(cls):
        
        if os.path.exists(DOCUMENTATON_PATH):
            utils.runSubprocess('git pull origin master', DOCUMENTATON_PATH)
        else:
            githubio.Githubio.cloneProject(
                'idiada_tools_doc', os.path.dirname(DOCUMENTATON_PATH))
    
    #---------------------------------------------------------------------------
    @classmethod
    def getListOfTools(cls):
        
        cls.synchronise()
        
        documentation = cls()
        
        return documentation.toolGroups
    
    #---------------------------------------------------------------------------
    @classmethod
    def checkUpdated(cls):
                
        stdout, _ = utils.runSubprocess('git log --oneline', DOCUMENTATON_PATH)
        commitCount = len(stdout.strip().split('\n'))
        
        cls.synchronise()
        
        stdout, _ = utils.runSubprocess('git log --oneline', DOCUMENTATON_PATH)
        
        newCommitCount = len(stdout.strip().split('\n'))
        
        if commitCount != newCommitCount:
            print('Documentation update found in the master repository.')
            return True
        else:
            print('Up-to-date')
            return False
    
    #---------------------------------------------------------------------------
    @classmethod
    def synchronise(cls):
        
        print('Synchronising tool documentation')
        
        githubio.Githubio.syncProject(DOCUMENTATON_PATH)
    
    #---------------------------------------------------------------------------
    @classmethod
    def commitToolAdded(cls, commitMessage):
                
        utils.runSubprocess('git commit -a -m "%s"' % commitMessage, DOCUMENTATON_PATH)
        
        githubio.Githubio.pushProject(
            os.path.basename(DOCUMENTATON_PATH), DOCUMENTATON_PATH)
            
#=============================================================================

    