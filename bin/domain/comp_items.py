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
        
        self.procedureItems = dict()
        
        self.mainModule = None
        self.mainModulePath = ''
        self.pyProjectPath = ''
        
        self._initialiseInstallationItems()
    
    #---------------------------------------------------------------------------
    
    def _initialiseInstallationItems(self):
        
        for itemName, installItem in bi.INSTALLER_PROCEDURE_ITEMS.iteritems():
            self.procedureItems[itemName] = installItem(self)
    
    #---------------------------------------------------------------------------
    
    def install(self):

        ''' This assumes that all checks have been passed so the new revision
        is made just when there was a new tag required. New revision is
        omitted otherwise.'''
        
        tagName = self.procedureItems[bi.VersionItem.NAME].tagName
        tagList = self.procedureItems[bi.VersionItem.NAME].tagList
        if tagName not in tagList:
            self.procedureItems[bi.DocumetationItem.NAME].updateDocString()
            
            self._createNewRevision(
                self.procedureItems[bi.VersionItem.NAME].tagName,
                self.procedureItems[bi.VersionItem.NAME].commitMessage,
                self.procedureItems[bi.VersionItem.NAME].filesToAdd)
         
        self.procedureItems[bi.InstallationSetupItem.NAME].installTypeItem.install(
            self.pyProjectPath,
            self.procedureItems[bi.VersionItem.NAME].tagName,
            self.procedureItems[bi.InstallationSetupItem.NAME].projectName,
            self.procedureItems[bi.DocumetationItem.NAME].docuGroup,
            self.procedureItems[bi.DocumetationItem.NAME].docuDescription)
        
    #---------------------------------------------------------------------------
    
    def setMainModule(self, mainModule, mainModulePath):
        
        self.mainModule = mainModule
        self.mainModulePath = mainModulePath
        self.pyProjectPath = os.path.dirname(os.path.dirname(mainModulePath))
    
    #---------------------------------------------------------------------------
    
    def _createNewRevision(self, tagName, commitMessage, newFileList):
                
        # add files
        for newFileName in newFileList:
            utils.runSubprocess('git add %s' % newFileName, cwd=os.path.dirname(
                os.path.dirname(self.mainModulePath)))
        
        # commit changes
        utils.runSubprocess('git commit -a -m "%s"' % commitMessage, cwd=os.path.dirname(
            os.path.dirname(self.mainModulePath)))        
        
        # add tag
        utils.runSubprocess('git tag %s' % tagName, cwd=os.path.dirname(
            os.path.dirname(self.mainModulePath)))
        
#=============================================================================
