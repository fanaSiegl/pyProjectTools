#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import getpass
import socket
import subprocess

from domain import utils
from domain import base_items as bi
    
#=============================================================================

class Installer(object):
    
    def __init__(self):
        
        self.mainModuleItem = bi.MainModuleItem()
        
        self.procedureItems = dict()
                
        self.mainModulePath = ''
        self.pyProjectPath = ''
        
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
         
        self._createMasterRepository()
    
    #---------------------------------------------------------------------------
    
    def setMainModule(self, mainModulePath):
        
        self.mainModuleItem.load(mainModulePath)
        
        # handle ANSA check type special behavior
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
        
        
#=============================================================================
