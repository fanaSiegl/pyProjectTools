#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
    
pyProjectTools
==============

.. image:: images/idiada_tools_logo.png
    :width: 200pt
    :align: center 
    
Is a package of tools which are supposed to be used to create, install and document python-based scripts.

Usage
-----

usage::

    pyProjectTools [-h] [-initiateAnsaToolkit] [-initiateDoc]
    
    optional arguments:
      -h, --help            show this help message and exit
      -initiateAnsaToolkit  Initiates ansa_toolkit data structure (a package for
                            user user script buttons, plugins and checks loading
                            to ANSA).
      -initiateDoc          Initiates IDIADA tools documentation data structure.


newPyProject
============

Creates a new python project template according to the given target project type. 
This project is supposed to be installed into standard project structure using pyProjectInstaller.  

* creates a default project structure
* creates a default sphinx documentation which will be generated from the documentation string of the main.py file
* initiates a git repository

Usage
-----

usage::

    newPyProject [-h] [-wrap script_path] [-ansaCheck] [-ansaButton] [-metaSession] projectName [project_path]
    
    positional arguments:
      projectName        Project name.
      project_path       New project location. (Default=Current directory)

    optional arguments:
      -h, --help         show this help message and exit
      -wrap script_path  Automatically wraps given executable script with a
                     newPyProject of given name. This project can be
                     directly installed using pyProjectInstaller.
      -ansaCheck         Creates an ANSA check template. Please be aware that in
                     order to use pyProjectInstaller the new created check
                     file name must contain a prefix: check_*.py
      -ansaButton        Creates an ANSA user script button template. This project
                     can be directly added to ANSA using pyProjectInstaller.
      -metaSession       Creates a META session template. This project can be
                     directly added to META using pyProjectInstaller.



pyProjectInstaller
==================

.. image:: images/pyProjectInstaller_01.png
    :width: 400pt
    :align: center
    
Python script for pyProject installation. According to the given 
installation type (executable script, ANSA button, ANSA check, META button) handles
all corresponding procedures:

* installs pyProject to the default project structure
* installs a default sphinx documentation based on main.py documentation string
* handles the git repository versions

Usage
-----

usage::

    pyProjectInstaller 

It is possible to use either "Local repository" or "Remote installation" 
as a source for installation.
    
    * Local repository type - pyProject to be installed has its repository (by script development)
    * Remote installation type - pyProject to be installed has been received from other business unit (by installation of an existing tool)


doc
===

Tool that generates a IDIADA tool documentation overview using SPHINX

Usage
-----

usage::

    doc [-h] [-init] [-update] [-sync]

    optional arguments:
      -h, --help  show this help message and exit
      -init       Clones existing IDIADA tool documentation files from github
                  master repository and sets remote origin.
      -update     Creates documentation html content from source documentation
                  files.
      -sync       Synchonises source documentation files with the master
                  repository.

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
        print('Cloning "ansaChecksPlistUpdater" from master repository.')
        
        INSTALL_PATHS = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_ANSA_CHECK']        
        if not os.path.exists(INSTALL_PATHS['CHECK_INSTALLER_PATH']):
            githubio.Githubio.cloneProject('ansaChecksPlistUpdater', INSTALL_PATHS['REPOS_PATH'])
        else:
            print('"ansaChecksPlistUpdater" already present: "%s"' % INSTALL_PATHS['CHECK_INSTALLER_PATH'])

    #---------------------------------------------------------------------------
    
    def initiateDoc(self):
        
        print('doc initialisation')
        
        doc.di.ToolDocumentation.initiateFromGithub()
        
        
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
