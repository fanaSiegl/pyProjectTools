#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
    
pyProjectTools
==============

Documentation defined in doc/

'''

#===============================================================================

APPLICATION_NAME = 'pyProjectTools'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for new python project installation.'

#===============================================================================

import os
import sys
import glob
import shutil
import argparse

from domain import utils
from interfaces import githubio

import doc
import newPyProject
import pyProjectInstaller

#=============================================================================

DEBUG = 0

#=============================================================================

class PyProjectTools(object):
    
    '''
pyProjectTools
==============

Description ...
    
    '''
    
    APPLICATION_NAME = 'pyProjectTools'
    
    def __init__(self):
        
        revision, modifiedBy, lastModified = utils.getVersionInfo()
        
        print('%s (%s)' % (self.APPLICATION_NAME, revision))
        print('MODIFIED BY: %s' % modifiedBy)
        print('LAST MODIFIED: %s' % lastModified)
        
        if DEBUG:
            print(PyProjectTools.__doc__)
            print(newPyProject.__doc__)
            print(pyProjectInstaller.__doc__)
            print(doc.__doc__)
    
    #---------------------------------------------------------------------------
    
    def showDoc(self):
        
        os.system('%s %s &' % (
            utils.getDocumentationBrowser(),
            os.path.join(utils.PATH_DOC, 'documentation.html')))
    
    #---------------------------------------------------------------------------
        
    def initiateAnsaToolkit(self):
          
        print('ansa_toolkit initialisation')    
                
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_BUTTON']
          
        # create directory structure for ansaTools
        print('Creating directory structure for ansaTools')
         
        ansaToolsLocation = INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']
        if not os.path.exists(ansaToolsLocation):
            ansaToolsSource = os.path.join(utils.PATH_RES, 'templates', 'ansaTools')
            shutil.copytree(ansaToolsSource, ansaToolsLocation, symlinks=True)
        else:
            print('Directory already present: "%s"' % ansaToolsLocation)
         
        # create directory structure for ansa_toolkit
        print('Creating directory structure for ansa_toolkit')
         
        ansaToolKitLocation = os.path.join(
            os.path.dirname(INSTALL_PATHS['PRODUCTIVE_VERSION_HOME']), 'ansa_toolkit')
        if not os.path.exists(ansaToolKitLocation):        
            ansaToolkitSource = os.path.join(utils.PATH_RES, 'templates', 'ansa_toolkit')
            shutil.copytree(ansaToolkitSource, ansaToolKitLocation, symlinks=True)
             
            # create default symbolic link
            symLink = os.path.join(ansaToolKitLocation, 'default')
            try:         
                currentVersion = glob.glob(os.path.join(ansaToolkitSource, 'V.*'))
                tag = os.path.basename(currentVersion[0])
                executable = os.path.join(ansaToolKitLocation, tag)
                if os.path.islink(symLink):
                    os.unlink(symLink)
                os.symlink(executable, symLink)
                 
            except Exception as e:
                print('Failed to set default ansa_toolkit version! (%s)' % str(e))
                                 
        else:
            print('Directory already present: "%s"' % ansaToolsLocation)
         
        # create directory for ansaTools repository
        print('Creating ansaTools repository directory')
         
        if not os.path.exists(INSTALL_PATHS['REPOS_PATH']):
            os.makedirs(INSTALL_PATHS['REPOS_PATH'])
        else:
            print('Directory already present: "%s"' % INSTALL_PATHS['REPOS_PATH'])
                         
        # create symbolic link to initiateAnsaToolkit
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_BASE']
         
        symLink = os.path.join(INSTALL_PATHS['GENERAL_PRODUCTIVE_VERSION_BIN'], 'initiateAnsaToolkit') 
        executable = os.path.join(ansaToolsLocation, 'initiateAnsaToolkit', 'initiateAnsaToolkit.py')
         
        if os.path.islink(symLink):
            os.unlink(symLink)
        os.symlink(executable, symLink)
                 
        # clone ansaChecksPlistUpdater
        print('Initiating ANSA "checks".')
        
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_CHECK']
        if not os.path.exists(INSTALL_PATHS['REPOS_PATH']):
            githubio.Githubio.cloneProject('checks', 
                os.path.dirname(INSTALL_PATHS['REPOS_PATH']))
<<<<<<< HEAD
        
        else:
            print('"checks" already present: "%s"' % INSTALL_PATHS['REPOS_PATH'])
            
            githubio.Githubio.syncProject(INSTALL_PATHS['REPOS_PATH'])
        
        self._installAnsaChecks()
            
    #---------------------------------------------------------------------------
    
    def _installAnsaChecks(self):
        
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_CHECK']
        
        # install last version
        pyProjectPath = INSTALL_PATHS['REPOS_PATH']
                
        installer = pyProjectInstaller.ci.Installer()
        ansaCheckInstallType = pyProjectInstaller.bi.InstallTypeAnsaCheck(installer)
        
        tagList, tagInfo = pyProjectInstaller.bi.LocalReposProjectSourceType.getTagInfo(pyProjectPath)
        
        revision = tagList[-1]
        
        if os.path.exists(os.path.join(INSTALL_PATHS['PRODUCTIVE_VERSION_HOME'], revision)):
            print('Check version up-to-date (%s).' % revision)
        else:
=======
        
        else:
            print('"checks" already present: "%s"' % INSTALL_PATHS['REPOS_PATH'])
            
            githubio.Githubio.syncProject(INSTALL_PATHS['REPOS_PATH'])
        
        self._installAnsaChecks()
            
    #---------------------------------------------------------------------------
    
    def _installAnsaChecks(self):
        
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_CHECK']
        
        # install last version
        pyProjectPath = INSTALL_PATHS['REPOS_PATH']
                
        installer = pyProjectInstaller.ci.Installer()
        ansaCheckInstallType = pyProjectInstaller.bi.InstallTypeAnsaCheck(installer)
        
        tagList, tagInfo = pyProjectInstaller.bi.LocalReposProjectSourceType.getTagInfo(pyProjectPath)
        
        revision = tagList[-1]
        
        if os.path.exists(os.path.join(INSTALL_PATHS['PRODUCTIVE_VERSION_HOME'], revision)):
            print('Check version up-to-date (%s).' % revision)
        else:
>>>>>>> 962bfea15e2c6f68ecfb77522ffba7fbfd795b83
            print('Installing ANSA checks: %s (%s)' % (revision, tagInfo[revision]))
            
            ansaCheckInstallType.install(
                pyProjectPath, revision, 'applicationName',
                'ANSA tools', 'IDIADA ANSA checks documentation.', 'docString')     

    #---------------------------------------------------------------------------
    
    def initiateDoc(self):
        
        print('doc initialisation')
        
        doc.di.ToolDocumentation.initiateFromGithub()
        
        documentation = doc.di.ToolDocumentation()
        documentation.create()
        documentation.show()
        
#=============================================================================

def main():
    
    parser = argparse.ArgumentParser(description=__doc__[:__doc__.find('Usage')],
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-initiateAnsaToolkit', action='store_true',
        help='Initiates ansa_toolkit data structure (a package for user user script buttons, \
        plugins and checks loading to ANSA).')
    parser.add_argument('-initiateDoc', action='store_true',
        help='Initiates IDIADA tools documentation data structure.')
    
    args = parser.parse_args()
    
    pyProjectTools = PyProjectTools()
    
    # initiate documentation from github
    if args.initiateAnsaToolkit:
        pyProjectTools.initiateAnsaToolkit()
    elif args.initiateDoc:
        pyProjectTools.initiateDoc()
    else:
        pyProjectTools.showDoc()
              
#=============================================================================

if __name__ == '__main__':
    
    main()
