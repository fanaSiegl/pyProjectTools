#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import string
import tempfile
import shutil
import imp

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
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos'
    VERSION_FILE = 'ini/version.ini'
    DOCUMENTATON_PATH = '/data/fem/+software/SKRIPTY/tools/python/tool_documentation/default'
    
    def __init__(self, parentInstaller):
        super(BaseInstallType, self).__init__()
        
        self.parentInstaller = parentInstaller
    
    #---------------------------------------------------------------------------
        
    def updateForInstallation(self):
        pass
    
    #---------------------------------------------------------------------------
    
    def install(self, pyProjectPath, revision, applicationName, docuGroup, docuDescription, docString):
        
        print 'Installing: %s' % self.NAME
        
        self.pyProjectPath = pyProjectPath
        self.targetDir = os.path.join(self.PRODUCTIVE_VERSION_HOME, applicationName, revision)
        self.applicationPath = os.path.join(self.PRODUCTIVE_VERSION_HOME, applicationName)
        self.revision = revision
        self.applicationName = applicationName
        self.docuGroup = docuGroup
        self.docuDescription = docuDescription
        self.docString = docString
        
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
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, self.executableName)
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
        
        # update index file
        newIndexLines = list()
        fi = open(os.path.join(SPHINX_SOURCE, 'index.rst'), 'rt')
        for line in fi.readlines():
            if line.startswith('.. automodule:: main'):
                newIndexLines.append('\n%s\n' % self.docString)
            else:
                newIndexLines.append(line)
        fi.close()
        
        fo = open(os.path.join(SPHINX_SOURCE, 'index.rst'), 'wt')
        for line in newIndexLines:
            fo.write(line)
        fo.close()
        
        # create revision history
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

    def __init__(self, parentInstaller):
        super(InstallTypeExecutable, self).__init__(parentInstaller)
        
        self.executableName = ''
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('executableName',
            'Name of the executable for the script')
        self.checker._checkSpacesInParam('executableName',
            'Name of the executable for the script')
    

#==============================================================================
@utils.registerClass
class InstallTypeAnsaButton(BaseInstallType):

    NAME = BaseInstallType.TYPE_ANSA_BUTTON
    PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python/ansaTools'
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos/ansaTools'
    PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/python/ansa_toolkit/default/ansa_toolkit/python_scripts'
    
    def __init__(self, parentInstaller):
        super(InstallTypeAnsaButton, self).__init__(parentInstaller)
        
        self.buttonGroupName = ''
        self.buttonName = ''
        self.execFunction = ''
        
        self.decoratorPresent = False
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('buttonGroupName',
            'ANSA User script button group name')
        self.checker._checkEmptyParam('buttonName', 'Tool button name')
        self.checker._checkSpacesInParam('buttonName', 'Tool button name')
        
    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print 'Releasing to the productive version'
        
        defaultDir = os.path.join(self.applicationPath, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, 'tool_%s.py' % self.buttonName)
        executable = os.path.join(defaultDir, self.EXECUTABLE)
        if os.path.islink(symLink):
            os.unlink(symLink)
        os.symlink(executable, symLink)
        
        os.chmod(symLink, 0775)
    
    #---------------------------------------------------------------------------
    
    def _insertAnsaButtonDecorator(self):
        
        if not self.decoratorPresent:
            self.parentInstaller.mainModuleItem.insertAnsaButtonDecorator(
                self.execFunction, self.buttonGroupName, self.buttonName)
    
    #---------------------------------------------------------------------------
        
    def updateForInstallation(self):
        
        self._insertAnsaButtonDecorator()
        
#==============================================================================
@utils.registerClass
class InstallTypeMeta(BaseInstallType):

    NAME = BaseInstallType.TYPE_META
    PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python/metaTools'
    REPOS_PATH = '/data/fem/+software/SKRIPTY/tools/repos/metaTools'
    PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/python/meta_toolkit/default/meta_toolkit/python_scripts'
    
    def __init__(self, parentInstaller):
        super(InstallTypeMeta, self).__init__(parentInstaller)
        
        self.toolbarName = ''
        self.buttonName = ''

    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('toolbarName', 'META Toolbar name')
        self.checker._checkEmptyParam('buttonName', 'Tool button name')

    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print 'Releasing to the productive version'
        
        defaultDir = os.path.join(self.applicationPath, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, 'tool_%s.py' % self.buttonName)
        executable = os.path.join(defaultDir, self.EXECUTABLE)
        if os.path.islink(symLink):
            os.unlink(symLink)
        os.symlink(executable, symLink)
        
        os.chmod(symLink, 0775)
        
        
#==============================================================================

class BaseInstallerProcedureItem(BaseParamItem):
    container = INSTALLER_PROCEDURE_ITEMS

    def __init__(self, parentInstaller):
        super(BaseInstallerProcedureItem, self).__init__()
        
        self.parentInstaller = parentInstaller
    
    #---------------------------------------------------------------------------
    
    def updateForInstallation(self):
        
        pass
        
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
        
    #---------------------------------------------------------------------------
        
    def updateForInstallation(self):
        
        self.installTypeItem.updateForInstallation()
             
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
        
    def updateForInstallation(self):
            
        # original string
        docString = self.parentInstaller.mainModuleItem.docString
        
        # no doc string present
        if not self.parentInstaller.mainModuleItem.hasDocString:
            self._createNewDocString(self.docString)        
        # existing string to be updated
        elif docString != self.docString:
            self._changeExistingDocString(self.docString)
        # doc string unchanged
        else:
            print 'Doc unchanged'
    
    #---------------------------------------------------------------------------
    
    def _createNewDocString(self, text):
        
        print 'Creating a new documentation string'
        
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
        
        print 'Updating existing documentation string'
        
        # original string
        docString = self.parentInstaller.mainModuleItem.docString
        
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
    
    def _checkSpacesInParam(self, paramName, description):
        
        value = getattr(self.installItem, paramName)
        
        if ' ' in value:
            message = '%s must not contain spaces!' % description
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
        
        docString = self.installItem.parentInstaller.mainModuleItem.docString
        
        if self.installItem.tagName in self.installItem.tagList:
            # no doc string present
            if not self.installItem.parentInstaller.mainModuleItem.hasDocString:
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

class MainModuleItem(object):
    
    def __init__(self):
        
        self._initiateParameters()
    
    #---------------------------------------------------------------------------
    
    def _initiateParameters(self):
                
        self.docHeaderLines = list()
        
        self.hasDocString = False
        self.docString = ''
        self.applicationName = ''
        self.documentationGroup = ''
        self.documentationDescription = ''
    
    #---------------------------------------------------------------------------
    
    def load(self, sourceMainPath):
        
        self.sourceMainPath = sourceMainPath
        self._initiateParameters()
    
        self._parse()
        self._findDocString()
                
    #---------------------------------------------------------------------------
    
    def _parse(self):
        
        fi = open(self.sourceMainPath, 'rt')
        
        self.content = fi.read()
        self.lines = self.content.split('\n')
        
        fi.close()
    
    #---------------------------------------------------------------------------
    
    def _findDocString(self):
        
        for line in self.lines:
            if line.startswith('import'):
                break
            else:
                self.docHeaderLines.append(line)
                
        tmpFile = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
        
        fo = open(tmpFile.name, 'wt')
        fo.write('\n'.join(self.docHeaderLines))
        fo.close()
        
        mainModule = imp.load_source(
            os.path.basename(tmpFile.name)[:-3], tmpFile.name)
        
        if mainModule.__doc__ is not None:
            self.docString = mainModule.__doc__
            self.hasDocString = True
        
        self._findProjectParams(mainModule)
    
    #---------------------------------------------------------------------------
    
    def _findProjectParams(self, mainModule):
        
        try:
            self.applicationName = mainModule.APPLICATION_NAME
        except AttributeError:
            pass
        try:
            self.documentationGroup = mainModule.DOCUMENTATON_GROUP
        except AttributeError:
            pass
        try:
            self.documentationDescription = mainModule.DOCUMENTATON_DESCRIPTION
        except AttributeError:
            pass
        
        if self.applicationName != '' and self.documentationGroup != '' and  self.documentationDescription != '':
            return
        
        # alternative search
        def getLineParamValue(line):
            parts = line.split('=')
            return parts[-1].strip()
        
        for line in self.lines:
            if line.startswith('APPLICATION_NAME') and self.applicationName == '':
                self.applicationName = getLineParamValue(line)
            elif line.startswith('DOCUMENTATON_GROUP') and self.documentationGroup == '':
                self.documentationGroup = getLineParamValue(line)
            elif line.startswith('DOCUMENTATON_DESCRIPTION') and self.documentationDescription == '':
                self.documentationDescription = getLineParamValue(line)
    
    #---------------------------------------------------------------------------
    
    def _stripFunctionParamString(self, string):
        
        
        string = string.strip().replace('"','')
        string = string.replace("'",'')
        return string
    
    #---------------------------------------------------------------------------
    
    def getListOfFunctions(self):
        
        functions = dict()
        for lineNo, line in enumerate(self.lines):
            if line.startswith('def'):
                parts = line.split('(')
                funcName = parts[0].replace('def', '')
                
                functions[funcName.strip()] = lineNo
        return functions
    
    #---------------------------------------------------------------------------
    
    def getListOfAnsaButtonDecoratedFunctions(self):
        
        functions = list()
        for lineNo, line in enumerate(self.lines):
            if line.startswith('def'):
                if self.lines[lineNo - 1].startswith('@ansa.session.defbutton'):
                    # decorator
                    parts = self.lines[lineNo - 1].split('(')
                    params = parts[1].replace(')', '')
                    paramParts = params.split(',')
                    group = self._stripFunctionParamString(paramParts[0])
                    buttonName = self._stripFunctionParamString(paramParts[1])
                    
                    # decorated function
                    parts = line.split('(')
                    funcName = parts[0].replace('def', '')
                    
                    funcName = self._stripFunctionParamString(funcName)
                    
                    functions.append({
                        funcName : [group, buttonName]})
                    
        return functions
    
    #---------------------------------------------------------------------------
    
    def insertAnsaButtonDecorator(self, execFunction, buttonGroupName, buttonName):
        
        listOfFuntions = self.getListOfFunctions()
        
        lineNo = listOfFuntions[execFunction]
        
        newLine = '@ansa.session.defbutton("%s", "%s")' % (
            buttonGroupName, buttonName)
        
        lines = self.lines[:]
        lines.insert(lineNo, newLine)
        
        fo = open(self.sourceMainPath, 'wt')
        for line in lines:
            fo.write('%s\n' % line)
        fo.close() 
                
        
#=============================================================================

