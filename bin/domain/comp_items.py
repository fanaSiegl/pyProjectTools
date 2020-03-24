#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import copy

from domain import utils
from domain import base_items as bi
from domain import doc_items as di

from interfaces import githubio
    
#=============================================================================

class Installer(object):
    
    def __init__(self):
        
        self.mainModuleItem = bi.MainModuleItem()
        
        self.procedureItems = dict()
                
        self.mainModulePath = ''
        self.pyProjectPath = ''
        self.projectSourceType = bi.LocalReposProjectSourceType
        self.toolGroups = None
        
        self._initialiseInstallationItems()
    
    #---------------------------------------------------------------------------
    
    def _initialiseInstallationItems(self):
        
        for itemName, installItem in bi.INSTALLER_PROCEDURE_ITEMS.items():
            self.procedureItems[itemName] = installItem(self)
    
    #---------------------------------------------------------------------------
    
    def install(self):
            
        ''' This assumes that all checks have been passed so the new revision
        is made just when there was a new tag required. New revision is
        omitted otherwise.'''
        
        # this will ensure that all procedure will be done prior to
        # creating a new revision
        for procedureItem in self.procedureItems.values():
            procedureItem.updateForInstallation()   
        
        # create revision only if source project type is local revision
        if self.projectSourceType is bi.LocalReposProjectSourceType:
            tagName = self.procedureItems[bi.VersionItem.NAME].tagName
            tagList = self.procedureItems[bi.VersionItem.NAME].tagList
            if tagName not in tagList:              
                self._createNewRevision(
                    self.procedureItems[bi.VersionItem.NAME].tagName,
                    self.procedureItems[bi.VersionItem.NAME].commitMessage,
                    self.procedureItems[bi.VersionItem.NAME].filesToAdd)
           
        self.procedureItems[bi.InstallationSetupItem.NAME].installTypeItem.install(
            self.pyProjectPath,
            self.procedureItems[bi.VersionItem.NAME].tagName,
            self.procedureItems[bi.InstallationSetupItem.NAME].projectName,
            self.procedureItems[bi.DocumetationItem.NAME].docuGroup,
            self.procedureItems[bi.DocumetationItem.NAME].docuDescription,
            self.procedureItems[bi.DocumetationItem.NAME].docString)
        
        # create master repository if not installing ANSA check
        if self.getCurrentInstallType() != bi.BaseInstallType.TYPE_ANSA_CHECK \
            and self.projectSourceType is not bi.RemoteInstallationProjectSourceType:
            
            self._createMasterRepository()
        
        # clean up temporary data
        self.projectSourceType.cleanUp()
    
    #---------------------------------------------------------------------------
    
    def setMainModule(self, mainModulePath):
        
        self.mainModuleItem.load(mainModulePath)
        
        # ANSA check type special behavior
        if self.getCurrentInstallType() == bi.BaseInstallType.TYPE_ANSA_CHECK:
        
            self.mainModulePath = bi.InstallTypeAnsaCheck.CHECK_INSTALLER_PATH
            self.pyProjectPath = os.path.dirname(
                os.path.dirname(self.mainModulePath))
            self.mainModuleItem.documentationDescription = 'IDIADA ANSA checks documentation.'
            self.mainModuleItem.documentationGroup = 'ANSA tools'
        else:
            self.mainModulePath = mainModulePath
            self.pyProjectPath = os.path.dirname(os.path.dirname(mainModulePath))
    
    #---------------------------------------------------------------------------
    
    def setProjectSourceType(self, sourceType):
        
        self.projectSourceType = sourceType
    
    #---------------------------------------------------------------------------
    
    def setToolGroups(self, toolGroups):
        
        self.toolGroups = copy.deepcopy(toolGroups)
        
        toolNames = list()
        for tools in self.toolGroups.values():
            toolNames.extend([tool.name for tool in tools])
        self.availableTools = set(toolNames)
            
    #---------------------------------------------------------------------------
    
    def getCurrentInstallType(self):
        
        return self.procedureItems[bi.InstallationSetupItem.NAME].installTypeItem.NAME
    
    #---------------------------------------------------------------------------
    
    def _createNewRevision(self, tagName, commitMessage, newFileList):
                
        # add files
        for newFileName in newFileList:
            print('Adding file to repository: %s' % newFileName)
            utils.runSubprocess('git add %s' % newFileName, cwd=os.path.dirname(
                os.path.dirname(self.mainModulePath)))
        
        # commit changes
        utils.runSubprocess('git commit -a -m "%s"' % commitMessage, cwd=os.path.dirname(
            os.path.dirname(self.mainModulePath)))        
        
        # add tag
        utils.runSubprocess('git tag %s' % tagName, cwd=os.path.dirname(
            os.path.dirname(self.mainModulePath)))
    
    #---------------------------------------------------------------------------
    
    def _createMasterRepository(self):
        
        print('Master repository synchronisation')
        
        reposPath = self.procedureItems[bi.InstallationSetupItem.NAME].installTypeItem.REPOS_PATH
        projectName = self.procedureItems[bi.InstallationSetupItem.NAME].projectName
        masterReposPath = os.path.join(reposPath, projectName)
        
        # check if repository exists
        if not os.path.isdir(masterReposPath):
            os.makedirs(masterReposPath)
            
            utils.runSubprocess('git init', cwd=masterReposPath)
        
        localReposPath = os.path.dirname(os.path.dirname(self.mainModulePath))
        
        # handle ANSA check type special behavior
        if not self.getCurrentInstallType() == bi.BaseInstallType.TYPE_ANSA_CHECK:
            utils.runSubprocess('git pull %s' % localReposPath, cwd=masterReposPath)
        
        utils.runSubprocess('git checkout master', cwd=masterReposPath)
        utils.runSubprocess('git fetch --tag %s' % localReposPath, cwd=masterReposPath)
        
        # synchronise with github if not there already
        if self.projectSourceType is not bi.MasterReposProjectSourceType:
                        
            if projectName in self.availableTools:
                print('Project exists in master repository')
                
                githubio.Githubio.pushProject(projectName, masterReposPath)
            else:
                print('Creating a new project in master repository')
                
                githubio.Githubio.createProject(projectName, masterReposPath)
                
                # add files to doc repository
                docSourceDir = os.path.join(di.SPHINX_SOURCE,
                    utils.getInstallTypePaths()['GENERAL']['LOCAL_DOCUMENTATION'],
                    self.procedureItems[bi.DocumetationItem.NAME].docuGroup.replace(' ', '_'),
                    projectName) + os.path.sep + '*'
                
                print('Adding new documentation files to doc repository: "%s"' % docSourceDir)
                
                utils.runSubprocess('git add %s' % docSourceDir, cwd=di.SPHINX_SOURCE)
        
        # synchronise documentation
        di.ToolDocumentation.commitToolAdded('Tool: %s (%s) installed.' % (
            projectName, self.procedureItems[bi.VersionItem.NAME].tagName))
    
    #---------------------------------------------------------------------------
    
 
        
        
#=============================================================================
