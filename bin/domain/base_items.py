#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import string
import shutil

from domain import utils


#=============================================================================

INSTALL_TYPES = dict()
INSTALLER_PROCEDURE_ITEMS = dict()

#==============================================================================

class InstallerCheckerException(Exception): pass

#==============================================================================

class InstallerException(Exception): pass

#==============================================================================

class BaseParamItem(object):
    
    def __init__(self):
        
        self.checker = BaseInstallItemChecker(self)
    
    #---------------------------------------------------------------------------
    
    def setParamValue(self, paramName, value):
#         print self, paramName, value
        setattr(self, paramName, value)
    
    #---------------------------------------------------------------------------
    
    def check(self):
        
        self.checker.initiateReport()
        
        self.addChecks()
        
        return self.checker.getReport()
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        pass
        
    
#==============================================================================

class BaseInstallType(BaseParamItem):
    container = INSTALL_TYPES
    TYPE_EXECUTABLE = 'Executable script'
    TYPE_ANSA_BUTTON = 'ANSA user script button'
    TYPE_META = 'META session'
    
    
    EXECUTABLE = 'bin/main.py'
    PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/bin'
    PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python'
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos/ansaTools'
    VERSION_FILE = 'ini/version.ini'
    DOCUMENTATON_PATH = '/data/fem/+software/SKRIPTY/tools/python/tool_documentation/default'
    
    #---------------------------------------------------------------------------
    
    def install(self, pyProjectPath, revision, applicationName, docuGroup, docuDescription):
        
        print 'Installing: %s' % self.NAME
        
        self.pyProjectPath = pyProjectPath
        self.targetDir = os.path.join(self.PRODUCTIVE_VERSION_HOME, applicationName, revision)
        self.applicationPath = os.path.join(self.PRODUCTIVE_VERSION_HOME, applicationName)
        self.revision = revision
        self.applicationName = applicationName
        self.docuGroup = docuGroup
        self.docuDescription = docuDescription
        
        self._createRevisionContents()
                
        self._createVersionFile()
        self._createDocumentation()
        self._cleanUp()
        
        self._installAsDefault()
        self._publishDocumentation()

    #---------------------------------------------------------------------------
    
    def _createVersionFile(self):
        
        print 'Updating a version file'
        
        modifiedBy, lastModified = self._getRevisionInfo()
        
        VERSION_FILE_TEMPLATE = '''[VERSION]
REVISION = ${revision}
AUTHOR = ${modifiedBy}
MODIFIED = ${lastModified}'''
        
        template = string.Template(VERSION_FILE_TEMPLATE)
        
        outputString = template.substitute(
            {'revision' : self.revision,
             'modifiedBy' : modifiedBy,
             'lastModified': lastModified})
        
        versionFile = open(os.path.join(self.targetDir, self.VERSION_FILE), 'wt')
        versionFile.write(outputString)
        versionFile.close()
        
    #---------------------------------------------------------------------------
    
    def _createRevisionContents(self):
        
        print 'Creating a revision content in: "%s"' % self.targetDir
        
        if os.path.isdir(self.targetDir): 
            raise InstallerException('Current revision exists already.')
        else:
            os.makedirs(self.targetDir)
        
        utils.runSubprocess('git clone . %s' % (self.targetDir), self.pyProjectPath)
        utils.runSubprocess('git checkout %s' % (self.revision), self.targetDir)
    
    #---------------------------------------------------------------------------
    
    def _cleanUp(self):
        
        print 'Cleaning up files'
        
        repositoryPath = os.path.join(self.targetDir, '.git')
        shutil.rmtree(repositoryPath)
            
        buildScript = os.path.join(self.targetDir, 'build.py')
        os.remove(buildScript)
    
        
    #---------------------------------------------------------------------------
    
    def _getRevisionInfo(self):
        
        print 'Gathering revision information'
        
        output, _ = utils.runSubprocess('git log %s -n 1' % self.revision, self.pyProjectPath)
        
        lines = output.split('\n')
        
        modifiedBy = lines[1].split(':')[1].strip()
        lastModified = ':'.join(lines[2].split(':')[1:]).strip()
        
        return modifiedBy, lastModified
    
    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print 'Releasing to the productive version'
        
        defaultDir = os.path.join(self.applicationPath, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, self.applicationName)
        executable = os.path.join(defaultDir, self.EXECUTABLE)
        if os.path.islink(symLink):
            os.unlink(symLink)
        os.symlink(executable, symLink)
        
        os.chmod(symLink, 0775)
    
    #---------------------------------------------------------------------------
    
    def _createDocumentation(self):
        
        print 'Creating local sphinx documentation'
        
        SPHINX_DOC = os.path.join(self.targetDir, 'doc', 'sphinx')
        SPHINX_SOURCE = os.path.join(SPHINX_DOC, 'source')
        SPHINX_DOCTREES = os.path.join(SPHINX_DOC, 'build', 'doctrees')
        SPHINX_HTML = os.path.join(SPHINX_DOC, 'build', 'html')
        SPHINX_BUILD = os.path.join(SPHINX_DOC, 'sphinx-build.py')
        GIT_REVISION_HISTORY = os.path.join(SPHINX_SOURCE, 'revision_history.rst')
        
        HEADER = '''
Revision history
================

Revision history graph::
    
    '''
        
        # create revision history
        stdout, _ = utils.runSubprocess('git log --graph --all --decorate --abbrev-commit',
            self.targetDir)
        lines = stdout.splitlines()
            
        fo = open(GIT_REVISION_HISTORY, 'wt')
        fo.write(HEADER)
            
        for line in lines:
            fo.write('   %s\n' % line)
        fo.close()
        
        # create local documentation
        utils.runSubprocess('python %s -b html -d %s %s %s' % (
            SPHINX_BUILD, SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML),
            self.targetDir)
    
    #---------------------------------------------------------------------------
    
    def _publishDocumentation(self):
        
        print 'Updating tool documentation'
        
        SPHINX_DOC = os.path.join(self.targetDir, 'doc', 'sphinx')
        SPHINX_HTML = os.path.join(SPHINX_DOC, 'build', 'html')
        
        SPHINX_INDEX = os.path.join(SPHINX_HTML, 'index.html')
        
        # copy to tool documentation
        docFileName = os.path.join(self.DOCUMENTATON_PATH, 'source',
            self.docuGroup.replace(' ', '_'), '%s.rst' % self.applicationName)
        
        if not os.path.exists(os.path.dirname(docFileName)):
            os.mkdir(os.path.dirname(docFileName))
        
        if os.path.exists(docFileName):
            os.remove(docFileName)
        
        fo = open(docFileName, 'wt')
        fo.write('.. _%s: %s\n\n' % (self.applicationName, SPHINX_INDEX))
        fo.write('`%s`_ - %s\n\n' % (self.applicationName, self.docuDescription))
        fo.close()
        
        # update tool documentation
        updateScriptPath = os.path.join(self.DOCUMENTATON_PATH, 'buildHtmlDoc.py')
        utils.runSubprocess(updateScriptPath)
        
    
    #---------------------------------------------------------------------------
                

#==============================================================================
@utils.registerClass
class InstallTypeExecutable(BaseInstallType):

    NAME = BaseInstallType.TYPE_EXECUTABLE
    PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python'
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos'
    PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/bin'

    def __init__(self):
        super(InstallTypeExecutable, self).__init__()
        
        self.executableName = ''
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('executableName',
            'Name of the executable for the script')

#==============================================================================
@utils.registerClass
class InstallTypeAnsaButton(BaseInstallType):

    NAME = BaseInstallType.TYPE_ANSA_BUTTON
    PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python/ansaTools'
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos/ansaTools'
    PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/python/ansa_toolkit/default/ansa_toolkit/python_scripts'
    
    def __init__(self):
        super(InstallTypeAnsaButton, self).__init__()
        
        self.buttonGroupName = ''
        self.buttonName = ''
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('buttonGroupName',
            'ANSA User script button group name')
        self.checker._checkEmptyParam('buttonName', 'Tool button name')
        
    
#==============================================================================
@utils.registerClass
class InstallTypeMeta(BaseInstallType):

    NAME = BaseInstallType.TYPE_META

    def __init__(self):
        super(InstallTypeMeta, self).__init__()
        
        self.toolbarName = ''
        self.buttonName = ''

    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('toolbarName', 'META Toolbar name')
        self.checker._checkEmptyParam('buttonName', 'Tool button name')
        
    
#==============================================================================

class BaseInstallerProcedureItem(BaseParamItem):
    container = INSTALLER_PROCEDURE_ITEMS

    def __init__(self, parentInstaller):
        super(BaseInstallerProcedureItem, self).__init__()
        
        self.parentInstaller = parentInstaller
        
#=============================================================================
@utils.registerClass
class InstallationSetupItem(BaseInstallerProcedureItem):
    
    NAME = 'Installation setup'
    
    def __init__(self, parentInstaller):
        super(InstallationSetupItem, self).__init__(parentInstaller)
        
        self.installTypeItem = None
        self.projectName = ''

    #---------------------------------------------------------------------------
    
    def check(self):
        
        return self.installTypeItem.check()
        
        
#=============================================================================
@utils.registerClass
class DocumetationItem(BaseInstallerProcedureItem):
    
    NAME = 'Documentation'
    
    def __init__(self, parentInstaller):
        super(DocumetationItem, self).__init__(parentInstaller)
        
        self.docuGroup = ''
        self.docuDescription = ''
        self.docString = ''
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('docuGroup', 'Documentation group')
        self.checker._checkEmptyParam('docuDescription', 'One line tool description')
        self.checker._checkEmptyParam('docString', 'Documentation string')
 
    #---------------------------------------------------------------------------
    
    def updateDocString(self):
        
        docString = self.parentInstaller.mainModule.__doc__
                        
        # no doc string present
        if docString is None:
            self._createNewDocString(self.docString)        
        # existing string to be updated
        elif docString != self.docString:
            self._changeExistingDocString(self.docString)
        # doc string unchanged
        else:
            print 'Doc unchanged'
    
    #---------------------------------------------------------------------------
    
    def _createNewDocString(self, text):
        
        fi = open(self.parentInstaller.mainModulePath, 'rt')
        lines = fi.readlines()
        fi.close()
        
        sheBangLines = list()
        contentLines = list()
        for lineNo, line in enumerate(lines):
            if line.startswith('#!'):
                sheBangLines.append(line)
            elif line.startswith('#') and lineNo <= 2:
                sheBangLines.append(line)
            else:
                contentLines.append(line)
                
        newContent = list()
        newContent.extend(sheBangLines)
        newContent.append("\n'''\n%s\n'''\n" % text)
        newContent.extend(contentLines)
        
        fo = open(self.parentInstaller.mainModulePath, 'wt')
        for line in newContent:
#             print line[:-1]
            fo.write(line)
        fo.close()
        
    #---------------------------------------------------------------------------
    
    def _changeExistingDocString(self, text):
        
        docString = self.parentInstaller.mainModule.__doc__
        
        fi = open(self.parentInstaller.mainModulePath, 'rt')
        content = fi.read()
        fi.close()
        
        newContent = content.replace(docString, text)
        
        fo = open(self.parentInstaller.mainModulePath, 'wt')
#         print newContent
        fo.write(newContent)
        fo.close()
           
#=============================================================================
@utils.registerClass
class VersionItem(BaseInstallerProcedureItem):
    
    NAME = 'Version'
    
    def __init__(self, parentInstaller):
        super(VersionItem, self).__init__(parentInstaller)
        
        self.tagName = ''
        self.commitMessage = ''
        self.filesToAdd = list()
        
        self.tagList = list()
        self.tagInfo = dict()
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('tagName', 'Tag name')
        self.checker._checkEmptyParam('commitMessage', 'Commit message')
        self.checker._checkNewRevisionFiles()
        self.checker._checkDocStringUpdate()
    
    #---------------------------------------------------------------------------
    
    def setCurrentTagList(self, pyProjectPath):
        
        stdout, stderr = utils.runSubprocess('git tag -n9', pyProjectPath)
        
        self.tagList = list()
        for line in stdout.splitlines():
            parts = line.strip().split()
            self.tagList.append(parts[0])
            self.tagInfo[parts[0]] = ' '.join(parts[1:])
    
    #---------------------------------------------------------------------------
    
    def getTagCommitMessage(self, tagName):
        
        if tagName in self.tagInfo:
            return self.tagInfo[tagName]
        else:
            return ''
    
    
#=============================================================================

class BaseInstallItemChecker(object):
    
    CHECK_TYPE_OK = 0
    CHECK_TYPE_WARNING = 1
    CHECK_TYPE_CRITICAL = 2
    
    def __init__(self, installItem):
        
        self.installItem = installItem
        self.report = list()
        self.status = self.CHECK_TYPE_OK
    
    #---------------------------------------------------------------------------
    
    def _checkEmptyParam(self, paramName, description):
        
        value = getattr(self.installItem, paramName)
        
        if len(value) == 0:
            message = '%s must not be empty!' % description
            self.report.append([self.CHECK_TYPE_CRITICAL, message])
            self.status += self.CHECK_TYPE_CRITICAL
        else:
            message = '%s check ok.' % description
            self.report.append([self.CHECK_TYPE_OK, message])
            
    #---------------------------------------------------------------------------
    
    def _checkNewRevisionFiles(self):
    
        if len(self.installItem.filesToAdd) > 0 and self.installItem.tagName in self.installItem.tagList:
            message = 'Files were added. New version must be made with a new tag!'
            self.report.append([self.CHECK_TYPE_CRITICAL, message])
            self.status += self.CHECK_TYPE_CRITICAL
            
    #---------------------------------------------------------------------------
        
    def _checkDocStringUpdate(self):
        
        ''' This checks whether any changes have been made in doc string while
        there is an existing tag selected. In that case a new tag must be made.'''
        
        documentationInstallItem = self.installItem.parentInstaller.procedureItems[DocumetationItem.NAME]
        
        docString = self.installItem.parentInstaller.mainModule.__doc__
        
        if self.installItem.tagName in self.installItem.tagList:
            # no doc string present
            if docString is None:
                message = 'Documentation string has been created. New version must be made with a new tag!'
                self.report.append([self.CHECK_TYPE_CRITICAL, message])
                self.status += self.CHECK_TYPE_CRITICAL       
            # existing string to be updated
            elif docString != documentationInstallItem.docString:
                message = 'Documentation string has been updated. New version must be made with a new tag!'
                self.report.append([self.CHECK_TYPE_CRITICAL, message])
                self.status += self.CHECK_TYPE_CRITICAL
            # doc string unchanged
            else:
                message = 'Documentation string unchanged.'
                self.report.append([self.CHECK_TYPE_OK, message])
            
    #---------------------------------------------------------------------------
    
    def initiateReport(self):
        
        self.report = list()
        self.status = self.CHECK_TYPE_OK
    
    #---------------------------------------------------------------------------
    
    def getReport(self):
        
        return self.status, self.report
    

#=============================================================================
