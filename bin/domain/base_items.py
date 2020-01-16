#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
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
    TYPE_META = 'META script'
    TYPE_ANSA_CHECK = 'ANSA check'
    
    INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_BASE']
    
    EXECUTABLE = 'bin/main.py'
    GENERAL_PRODUCTIVE_VERSION_BIN = INSTALL_PATHS['GENERAL_PRODUCTIVE_VERSION_BIN']
    PRODUCTIVE_VERSION_BIN = INSTALL_PATHS['PRODUCTIVE_VERSION_BIN']
    PRODUCTIVE_VERSION_HOME = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']
    REPOS_PATH = INSTALL_PATHS['REPOS_PATH']
    VERSION_FILE = 'ini/version.ini'
    DOCUMENTATON_PATH = INSTALL_PATHS['DOCUMENTATON_PATH']
    
    SOURCE_FILE_FILTER = 'pyProject main.py (main.py)'
    
    def __init__(self, parentInstaller):
        super(BaseInstallType, self).__init__()
        
        self.parentInstaller = parentInstaller
    
    #---------------------------------------------------------------------------
    
    def getTargetDir(self):
        
        return self.PRODUCTIVE_VERSION_HOME
    
    #---------------------------------------------------------------------------
    
    def getProjectNameFromSourceFile(self, fileName):
        
        return os.path.basename(os.path.dirname(os.path.dirname(str(fileName))))
        
    #---------------------------------------------------------------------------
        
    def updateForInstallation(self):
        pass
    
    #---------------------------------------------------------------------------
    
    def install(self, pyProjectPath, revision, applicationName, docuGroup, docuDescription, docString):
        
        print('Installing: %s' % self.NAME)
        
        self.pyProjectPath = pyProjectPath
        self.targetDir = os.path.join(self.getTargetDir(), applicationName, revision)
        self.applicationPath = os.path.join(self.getTargetDir(), applicationName)
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
        
        print('Updating a version file')
        
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
        
        print('Creating a revision content in: "%s"' % self.targetDir)
        
        if os.path.isdir(self.targetDir): 
            raise InstallerException('Current revision exists already.')
        else:
            os.makedirs(self.targetDir)
        
        utils.runSubprocess('git clone . %s' % (self.targetDir), self.pyProjectPath)
        utils.runSubprocess('git checkout %s' % (self.revision), self.targetDir)
    
    #---------------------------------------------------------------------------
    
    def _cleanUp(self):
        
        print('Cleaning up files')
        
        repositoryPath = os.path.join(self.targetDir, '.git')
        shutil.rmtree(repositoryPath)
            
        buildScript = os.path.join(self.targetDir, 'build.py')
        
        if os.path.isfile(buildScript):
            os.remove(buildScript)
        
    #---------------------------------------------------------------------------
    
    def _getRevisionInfo(self):
        
        print('Gathering revision information')
        
        output, _ = utils.runSubprocess('git log %s -n 1' % self.revision, self.pyProjectPath)
        
        lines = output.split('\n')
        
        modifiedBy = lines[1].split(':')[1].strip()
        lastModified = ':'.join(lines[2].split(':')[1:]).strip()
        
        return modifiedBy, lastModified
    
    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print('Releasing to the productive version')
        
        defaultDir = os.path.join(self.applicationPath, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, self.executableName)
        executable = os.path.join(defaultDir, self.EXECUTABLE)
        
        # delete existing bin link
        if os.path.islink(symLink):
            os.unlink(symLink)
        elif os.path.isfile(symLink):
            os.remove(symLink)
                
        # try to find python environment executable
        envExecutable = utils.getEnvironmentExecutable(os.path.join(defaultDir, 'ini'))
        if envExecutable is None:
            os.symlink(executable, symLink)
        else:
            fo = open(symLink, 'wt')
            fo.write('#!/usr/bin/bash\n')
            fo.write('%s %s' % (envExecutable, executable))
            fo.close()
            
        os.chmod(symLink, 0o775)
    
    #---------------------------------------------------------------------------
    
    def _createDocumentation(self):
        
        print('Creating local sphinx documentation')
        
        SPHINX_DOC = os.path.join(self.targetDir, 'doc', 'sphinx')
        SPHINX_SOURCE = os.path.join(SPHINX_DOC, 'source')
        SPHINX_DOCTREES = os.path.join(SPHINX_DOC, 'build', 'doctrees')
        SPHINX_HTML = os.path.join(SPHINX_DOC, 'build', 'html')
        GIT_REVISION_HISTORY = os.path.join(SPHINX_SOURCE, 'revision_history.rst')
                
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
        
        # create local documentation respecting target environment 
        envExecutable = utils.getEnvironmentExecutable(
            os.path.join(self.targetDir, 'ini'))
        if envExecutable is not None:
            utils.runSubprocess('%s -b html -d %s %s %s' % (
                os.path.join(os.path.dirname(envExecutable), 'sphinx-build'), 
                SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))
        else:
            utils.runSubprocess('sphinx-build -b html -d %s %s %s' % (
                SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))
        
        # create a link
        linkPath = os.path.join(self.targetDir, 'doc', 'documentation.html') 
        if not os.path.islink(linkPath):
            os.symlink('.' + os.sep + os.path.join('sphinx', 'build', 'html', 'index.html'),
                linkPath)
    
    #---------------------------------------------------------------------------
    
    def _publishDocumentation(self):
        
        print('Updating tool documentation')
        
        localLocation = utils.getInstallTypePaths()['GENERAL']['LOCAL_DOCUMENTATION']
        
        SPHINX_LOCAL_DOC_SOURCE = os.path.join(self.targetDir, 'doc', 'sphinx', 'source')
    
        SPHINX_INDEX = os.path.join(localLocation,
            self.docuGroup.replace(' ', '_'), self.applicationName,
            '%s.html' % self.applicationName)
        
        # copy to tool documentation
        # create main link file
        SPHINX_GLOBAL_DOC_SOURCE = os.path.join(self.DOCUMENTATON_PATH,
            'res', 'source', localLocation,       
            self.docuGroup.replace(' ', '_'), self.applicationName)
        docFileName = os.path.join(SPHINX_GLOBAL_DOC_SOURCE,
            '%s.txt' % self.applicationName)
            
        if os.path.exists(SPHINX_GLOBAL_DOC_SOURCE):
            shutil.rmtree(SPHINX_GLOBAL_DOC_SOURCE)
        
        # copy doc source files
        shutil.copytree(SPHINX_LOCAL_DOC_SOURCE, SPHINX_GLOBAL_DOC_SOURCE)
        
         
        fo = open(docFileName, 'wt')
        fo.write('.. _%s: ./%s\n\n' % (self.applicationName, SPHINX_INDEX))
        fo.write('`%s`_ - %s\n\n' % (self.applicationName, self.docuDescription))
        fo.close()
    
        # update index file
        newIndexLines = list()
        fi = open(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst'), 'rt')
        for line in fi.readlines():
            if line.startswith('.. automodule:: main'):
                newIndexLines.append('\n%s\n' % self.docString)
            else:
                newIndexLines.append(line)
        fi.close()
        
        fo = open(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, '%s.rst' % self.applicationName), 'wt')
        for line in newIndexLines:
            fo.write(line)
        fo.close()
            
        # delete redundant files
        if os.path.isfile(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'conf.py')):
            os.remove(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'conf.py'))
        if os.path.isfile(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst')):
            os.remove(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst'))
        
        # update tool documentation
        utils.runSubprocess(os.path.join(self.GENERAL_PRODUCTIVE_VERSION_BIN, 'doc-update'))
    
    #---------------------------------------------------------------------------
                

#==============================================================================
@utils.registerClass
class InstallTypeExecutable(BaseInstallType):

    NAME = BaseInstallType.TYPE_EXECUTABLE
    INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_EXECUTABLE']
    
    PRODUCTIVE_VERSION_HOME = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']
    REPOS_PATH = INSTALL_PATHS['REPOS_PATH']
    PRODUCTIVE_VERSION_BIN = INSTALL_PATHS['PRODUCTIVE_VERSION_BIN']

    def __init__(self, parentInstaller):
        super(InstallTypeExecutable, self).__init__(parentInstaller)
        
        self.executableName = ''
        self.codeLanguage = 'python'

    #---------------------------------------------------------------------------
    
    def getTargetDir(self):
        
        return os.path.join(self.PRODUCTIVE_VERSION_HOME, self.codeLanguage)
        
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
    INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_BUTTON']
    
    PRODUCTIVE_VERSION_HOME = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']#'/data/fem/+software/SKRIPTY/tools/python/ansaTools'
    REPOS_PATH = INSTALL_PATHS['REPOS_PATH']#'/data/fem/+software/SKRIPTY/tools/repos/ansaTools'
    PRODUCTIVE_VERSION_BIN = INSTALL_PATHS['PRODUCTIVE_VERSION_BIN']#'/data/fem/+software/SKRIPTY/tools/python/ansa_toolkit/default/ansa_toolkit/python_scripts'
    
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
        
        print('Releasing to the productive version')
        
        defaultDir = os.path.join(self.applicationPath, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        # create link file which will be loaded by ansaTookit
        docString = self.parentInstaller.procedureItems[DocumetationItem.NAME].docString
        
        BUTTON_LINK_TEMPLATE = '''# PYTHON script
# -*- coding: utf-8 -*-

${docString}

import os
import sys

import ansa

# ==============================================================================

BUTTON_NAME = '${buttonName}'
BUTTON_GROUP_NAME = '${buttonGroupName}'
APPLICATION_NAME = '${applicationName}'
PATH_TOOLS = os.environ['ANSA_TOOLS']
PATH_TOOL = os.path.join(PATH_TOOLS, APPLICATION_NAME, 'default', 'bin')

# ==============================================================================
@ansa.session.defbutton(BUTTON_GROUP_NAME, BUTTON_NAME, __doc__)
def ${applicationName}RunFcn():
    
    sys.path.append(PATH_TOOL)
    ansa.ImportCode(os.path.join(PATH_TOOL, 'main.py'))
    mainModule = main

    mainModule.${execFunction}()

    sys.path.remove(PATH_TOOL)

# ==============================================================================

'''
                
        template = string.Template(BUTTON_LINK_TEMPLATE)
        
        outputString = template.safe_substitute(
            {'docString' : "'''\n%s\n'''" % docString,
             'buttonName' : self.buttonName,
             'buttonGroupName' : self.buttonGroupName,
             'applicationName' : self.applicationName,
             'execFunction' : self.execFunction})
        
        symLink = os.path.join(self.PRODUCTIVE_VERSION_BIN, 'tool_%s.py' % self.applicationName)
        
        fo = open(symLink, 'wt')
        fo.write(outputString)
        fo.close()

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
class InstallTypeAnsaCheck(BaseInstallType):
    
    NAME = BaseInstallType.TYPE_ANSA_CHECK
    INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_CHECK']
    
    SOURCE_FILE_FILTER = 'ANSA check_*.py (check_*.py)'

#TODO: installation is made from repository - change it to "update_ansa_checks" productive version
    
    CHECK_INSTALLER_PATH = INSTALL_PATHS['CHECK_INSTALLER_PATH']#'/data/fem/+software/SKRIPTY/tools/repos/ansaChecksPlistUpdater/bin/main.py'
    CHECK_INSTALLER_CHECK_PATH = INSTALL_PATHS['CHECK_INSTALLER_CHECK_PATH']#'/data/fem/+software/SKRIPTY/tools/repos/ansaChecksPlistUpdater/res/checks'
    PRODUCTIVE_VERSION_HOME = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']#'/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/'
    
    #---------------------------------------------------------------------------
    
    def getProjectNameFromSourceFile(self, fileName):
        
        projectName = os.path.basename(str(fileName))
        projectName = os.path.splitext(projectName)[0]
        
        return projectName.replace('check_', '')
    
    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkAnsaCheckScript()
    
    #---------------------------------------------------------------------------
    
    def install(self, pyProjectPath, revision, applicationName, docuGroup, docuDescription, docString):
        
        print('Installing: %s' % self.NAME)
        
        self.targetDir = os.path.join(self.getTargetDir(), revision)
        self.revision = revision
        self.docuGroup = docuGroup
        self.docuDescription = docuDescription
        
        # read original docString from check parent updater
        checksParentUpdater = MainModuleItem()
        checksParentUpdater.load(self.CHECK_INSTALLER_PATH)
        self.docString = checksParentUpdater.docString
        
        self._createDirs()
        self._installAsDefault()
        self._createRevisionContents()
        
        self.targetDir = os.path.dirname(os.path.dirname(self.CHECK_INSTALLER_PATH))
        self._createDocumentation()
        
        self.applicationName = 'checks'
        self._publishDocumentation()
        
    #---------------------------------------------------------------------------
    
    def _createDirs(self):
        
        if os.path.isdir(self.targetDir): 
            raise InstallerException('Current revision exists already.')
        else:
            os.makedirs(self.targetDir)
            
    #---------------------------------------------------------------------------
    
    def _createRevisionContents(self):

        print('Creating a revision content in: "%s"' % self.targetDir)
        
        stdout, _ = utils.runSubprocess('%s -copy %s' % (self.CHECK_INSTALLER_PATH, self.targetDir))
        
        print(stdout)

    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print('Releasing to the productive version')
        
        defaultDir = os.path.join(self.getTargetDir(), 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
         
    #---------------------------------------------------------------------------
         
    def updateForInstallation(self):
         
        ''' This is a workaround for the proper ANSA check installation
        based check wrap to the one ansaChecksPlistUpdater tool. '''
        
        dst = os.path.join(self.CHECK_INSTALLER_CHECK_PATH,
            os.path.basename(self.parentInstaller.mainModuleItem.sourceMainPath)) 
        
        if os.path.isfile(dst):
            os.remove(dst)
        
        shutil.copy(self.parentInstaller.mainModuleItem.sourceMainPath,
            dst)
                
    
#==============================================================================
@utils.registerClass
class InstallTypeMeta(BaseInstallType):

    NAME = BaseInstallType.TYPE_META
    INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_META']
    
    PRODUCTIVE_VERSION_HOME = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']
    REPOS_PATH = INSTALL_PATHS['REPOS_PATH']
    PRODUCTIVE_VERSION_BIN = INSTALL_PATHS['PRODUCTIVE_VERSION_BIN']
    
    def __init__(self, parentInstaller):
        super(InstallTypeMeta, self).__init__(parentInstaller)
        
        self.toolbarName = ''
#        self.buttonName = ''

    #---------------------------------------------------------------------------
    
    def addChecks(self):
        
        self.checker._checkEmptyParam('toolbarName', 'META Toolbar name')
#         self.checker._checkEmptyParam('buttonName', 'Tool button name')
        self.checker._checkMetaToolbarName()

    #---------------------------------------------------------------------------
    
    def _installAsDefault(self):
        
        print('Releasing to the productive version')
        
        defaultDir = os.path.join(self.getTargetDir(), self.applicationName, 'default')
        
        if os.path.islink(defaultDir):
            os.unlink(defaultDir)
        os.symlink(self.revision, defaultDir)
        
        defaultFileName = os.path.join(
            self.PRODUCTIVE_VERSION_BIN, 'toolbar_%s.path' % self.applicationName)
                
        fo = open(defaultFileName, 'wt')
        fo.write('${toolbar_folder}%s/default/bin/toolbar.defaults' % self.applicationName)
        fo.close()
    
                
        
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
            print('Doc unchanged')
        
        # check corresponding executable for sphinx-build 
        # (to ensure that all modules are present in the interpreter for automodule::)
        projectPath = os.path.dirname(os.path.dirname(
            self.parentInstaller.mainModuleItem.sourceMainPath))
        configFilePath = os.path.join(projectPath, 'ini')
        envExecutable = utils.getEnvironmentExecutable(configFilePath)
        if envExecutable is not None:
            print('Updating external executable for sphinx documentation generation.')
            try:
                buildHtmlFileName = os.path.join(projectPath,
                    'doc', 'sphinx', 'buildHtmlDoc.py')
                
                fi = open(buildHtmlFileName, 'rt')
                lines = fi.readlines()
                fi.close()
                
                for lineNo, line in enumerate(lines):
                    if line.startswith("os.system('sphinx-build "):
                        newLine = line.replace('sphinx-build', 
                            os.path.join(os.path.dirname(envExecutable), 'sphinx-build'))
                        lines[lineNo] = newLine
                    elif line.startswith("os.system('"):
                        index =  line.find('sphinx-build')
                        newLine = "os.system('%s/" % os.path.dirname(envExecutable) + line[index:]                        
                        lines[lineNo] = newLine
                    
                fo = open(buildHtmlFileName, 'wt')
                for line in lines:
                    fo.write(line)
                fo.close()
            except Exception as e:
                print('Failed to update external executable for documentation \
                generation! (%s)' % str(e))
            
    #---------------------------------------------------------------------------
    
    def _createNewDocString(self, text):
        
        print('Creating a new documentation string')
        
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
            fo.write(line)
        fo.close()
        
    #---------------------------------------------------------------------------
    
    def _changeExistingDocString(self, text):
        
        print('Updating existing documentation string')
        
        # original string
        docString = self.parentInstaller.mainModuleItem.docString
        
        fi = open(self.parentInstaller.mainModulePath, 'rt')
        content = fi.read()
        fi.close()
        
        newContent = content.replace(docString, text)
        
        fo = open(self.parentInstaller.mainModulePath, 'wt')
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
        self.checker._checkAnsaCheckNewTag()
    
    #---------------------------------------------------------------------------
    
    def setCurrentTagList(self, pyProjectPath):
        
        stdout, stderr = utils.runSubprocess('git tag -n9', pyProjectPath)
        
        self.tagList = list()
        for line in stdout.splitlines():
            if not line.startswith('V'):
                continue
            parts = line.strip().split()
            self.tagList.append(parts[0])
            self.tagInfo[parts[0]] = ' '.join(parts[1:])
    
    #---------------------------------------------------------------------------
    
    def getTagCommitMessage(self, tagName):
        
        if tagName in self.tagInfo:
            return self.tagInfo[tagName]
        else:
            return ''
    
    
    #---------------------------------------------------------------------------
         
    def updateForInstallation(self):
        
        # add a file automatically in case of an ANSA check
        if self.parentInstaller.procedureItems[InstallationSetupItem.NAME].installTypeItem.NAME == BaseInstallType.TYPE_ANSA_CHECK:
            self.filesToAdd.append(self.parentInstaller.mainModuleItem.sourceMainPath)
    
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
    
    def _checkAnsaCheckScript(self):
                
        if self.installItem.parentInstaller.mainModuleItem.checkAnsaCheckParametersPresence():
            message = '"checkDescription" present in the check file ok.'
            self.report.append([self.CHECK_TYPE_OK, message])
        else:
            message = 'There is no "checkDescription" present in the check file!'
            self.report.append([self.CHECK_TYPE_CRITICAL, message])
            self.status += self.CHECK_TYPE_CRITICAL
    
    #---------------------------------------------------------------------------
    
    def _checkAnsaCheckNewTag(self):
        
        if self.installItem.parentInstaller.getCurrentInstallType() == BaseInstallType.TYPE_ANSA_CHECK:
            
            tagName = self.installItem.tagName
            tagList = self.installItem.tagList
            if tagName in tagList:
                message = 'You have to create a new version in order to add a new ANSA check!'
                self.report.append([self.CHECK_TYPE_CRITICAL, message])
                self.status += self.CHECK_TYPE_CRITICAL
            else:
                message = 'New version check ok.'
                self.report.append([self.CHECK_TYPE_OK, message])
    
    
    #---------------------------------------------------------------------------

    def _checkMetaToolbarName(self):
        
        toolbarDefaultsFileName = os.path.join(
            os.path.dirname(self.installItem.parentInstaller.mainModuleItem.sourceMainPath),
            'toolbar.defaults')
        
        if not os.path.exists(toolbarDefaultsFileName):
            message = 'toolbar.defaults "%s" file does not exist!' % toolbarDefaultsFileName
            self.report.append([self.CHECK_TYPE_CRITICAL, message])
            self.status += self.CHECK_TYPE_CRITICAL
        else:
            message = 'toolbar.defaults name ok.'
            self.report.append([self.CHECK_TYPE_OK, message])
        
            fi = open(toolbarDefaultsFileName, 'rt')
            for line in fi.readlines():
                if line.startswith('toolbar start ') and self.installItem.toolbarName not in line:
                    message = 'Non-consistent toolbar name found in "toolbar.defaults"! Given: "%s", found: "%s"' % (
                        self.installItem.toolbarName, line.strip().replace('toolbar start ', ''))
                    self.report.append([self.CHECK_TYPE_CRITICAL, message])
                    self.status += self.CHECK_TYPE_CRITICAL
                    break
            fi.close()

#         return
#     
#         existingToolbarNames = list()
#         for toolbarName in os.listdir(self.installItem.PRODUCTIVE_VERSION_HOME):
#             path = os.path.join(self.installItem.PRODUCTIVE_VERSION_HOME, toolbarName)
#             if os.path.isdir(path):
#                 existingToolbarNames.append(toolbarName)
#             
#         if self.installItem.toolbarName in existingToolbarNames:
#             message = 'Given toolbar name: "%s" already exists!' % self.installItem.toolbarName
#             self.report.append([self.CHECK_TYPE_CRITICAL, message])
#             self.status += self.CHECK_TYPE_CRITICAL
#         else:
#             message = 'Toolbar name ok.'
#             self.report.append([self.CHECK_TYPE_OK, message])
        
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
        
        self.ansaButtonName = ''
        self.ansaButtonGroupName = ''
        
        self.metaToolbarName = ''
    
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
            if line.startswith('import') or (line.startswith('from ') and 'import' in line):
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
        
        attributeMap = {
            'applicationName'       : 'APPLICATION_NAME',
            'documentationGroup'    : 'DOCUMENTATON_GROUP',
            'documentationDescription': 'DOCUMENTATON_DESCRIPTION',
            'ansaButtonName'        : 'BUTTON_NAME',
            'ansaButtonGroupName'   : 'BUTTON_GROUP_NAME',
            'metaToolbarName'       : 'TOOLBAR_NAME'
            }
        
        # try native import
        for attrName, mainAttrName in attributeMap.items():
            try:
                setattr(self, attrName, getattr(mainModule, mainAttrName))
            except Exception:
                pass
        
        # alternative search
        def getLineParamValue(line):
            parts = line.split('=')
            return parts[-1].strip()
        
        for line in self.lines:
            for attrName, mainAttrName in attributeMap.items():
                if line.startswith(mainAttrName) and getattr(self, attrName) == '':
                    setattr(self, attrName,
                        self._stripFunctionParamString(getLineParamValue(line)))   
    
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
                    
                    # check if kept default
                    if group == 'BUTTON_GROUP_NAME':
                        group = self.ansaButtonGroupName
                    if buttonName == 'BUTTON_NAME':
                        buttonName = self.ansaButtonName
                    
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
    
    #---------------------------------------------------------------------------
    
    def checkAnsaCheckParametersPresence(self):
        
        for line in self.lines:
            parts = line.split()
            if len(parts) > 0:
                if parts[0] == 'checkDescription':
                    return True
        
        return False 
                
        
#=============================================================================

