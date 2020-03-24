#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
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

'''

#===============================================================================

APPLICATION_NAME = 'newPyProject'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for new python project creation'

#===============================================================================

import os
import sys
import stat
import string
import argparse
import shutil

from domain import utils

#===============================================================================
    
class ProjectCreator(object):
    
    APPLICATION_NAME = 'newPyProject'
    PROJECT_STRUCTURE = 'new_project_structure'
    BUTTON_PROJECT_STRUCTURE = 'new_ansa_button_project_structure'
    META_SESSION_PROJECT_STRUCTURE = 'new_meta_session_project_structure'
    
    def __init__(self, projectName, path):
        
        self.projectName = projectName
        self.path = path
        self.projectPath = os.path.join(path, self.projectName) 
    
    #---------------------------------------------------------------------------
    
    def createNewPyProject(self):
        
        self._create(self.PROJECT_STRUCTURE)        
        self._createSphinxDocIndex()
        self._initRepository()
        
        print('Project: "%s" created.' % self.projectName)    
    
    #---------------------------------------------------------------------------
    
    def wrapExecutable(self, executablePath):
        
        self._create(self.PROJECT_STRUCTURE)
        self._wrapExecutable(executablePath)
        self._createSphinxDocIndex()
        self._initRepository()
        
        print('Project: "%s" created.' % self.projectName)
    
    #---------------------------------------------------------------------------
    
    def createAnsaCheck(self):
        
        fi = open(os.path.join(utils.PATH_RES, 'templates', 'new_ansa_check', 'ansa_check_template.py'), 'rt')
        templateString = fi.read()
        fi.close()
        
        template = string.Template(templateString)
        newContent = template.safe_substitute(ansaCheckName=self.projectName)
        
        checkFilePath = os.path.join(self.projectPath, '%s.py' % self.projectName)
        
        if not os.path.exists(os.path.dirname(checkFilePath)):
            os.makedirs(os.path.dirname(checkFilePath))
        
        fo = open(checkFilePath, 'wt')
        fo.write(newContent)
        fo.close()
        
        print('ANSA check: "%s" created.' % os.path.join(
            self.projectPath, '%s.py' % self.projectName))
    
    #---------------------------------------------------------------------------
    
    def createAnsaButton(self):
        
        self._create(self.BUTTON_PROJECT_STRUCTURE)        
        self._createSphinxDocIndex()
        self._initRepository()
        
        print('Project: "%s" created.' % self.projectName)  
    
    #---------------------------------------------------------------------------
    
    def createMetaSession(self):
        
        self._create(self.META_SESSION_PROJECT_STRUCTURE)
        self._createSphinxDocIndex()
        self._initRepository()
        
        print('Project: "%s" created.' % self.projectName)
    
    #---------------------------------------------------------------------------
    
    def _create(self, projectStructure):
        
        print('Creating project content')
        
        if os.path.exists(self.projectPath):
            print('Project already exists: "%s"' % self.projectPath)
            return
        
        sourceProject = os.path.join(utils.PATH_RES, 'templates', projectStructure)
        
        shutil.copytree(sourceProject, self.projectPath)
    
    #---------------------------------------------------------------------------
    
    def _initRepository(self):
        
        print('Initialising project repository')
        
        os.chdir(self.projectPath)
        
        os.system('git init')
        os.system('git add *')
        os.system('git commit -m "Initial commit."')
    
    #---------------------------------------------------------------------------
    
    def _createSphinxDocIndex(self):
        
        
        SPHINX_SOURCE = os.path.join(self.projectPath, 'doc', 'sphinx', 'source')
        if not os.path.exists(SPHINX_SOURCE):
            os.mkdir(SPHINX_SOURCE)
        
        # create index
        fo = open(os.path.join(SPHINX_SOURCE, 'index.rst'), 'wt')
#         fo.write('%s documentation\n' % self.projectName)
#         fo.write((len(self.projectName) + 14)*'=' + '\n\n')
        fo.write('.. toctree::\n')
        fo.write('   :maxdepth: 2\n\n')
        fo.write('.. automodule:: main\n\n')
        fo.write('Revision history\n')
        fo.write('----------------\n\n')
        fo.write('Application revision history overview.\n\n')
        fo.write('.. toctree::\n')
        fo.write('   :maxdepth: 2\n\n')
        fo.write('   revision_history.rst\n')
        fo.close()
        
        # create conf.py
        fi = open(os.path.join(utils.PATH_RES, 'templates', 'conf.py'), 'rt')
        lines = fi.readlines()
        fi.close()
        
        for lineNo, line in enumerate(lines):
            if line.startswith('TOOL_NAME = '):
                newToolDefinition = "TOOL_NAME = '%s'\n" % self.projectName
                lines[lineNo] = newToolDefinition 
                break
        
        confFileName = os.path.join(SPHINX_SOURCE, 'conf.py')
        
        fo = open(confFileName, 'wt')
        for line in lines:
            fo.write(line)
        fo.close()
    
    #---------------------------------------------------------------------------
    
    def _wrapExecutable(self, executablePath):
        
        baseExecutableName = os.path.basename(executablePath)
        destExecutablePath = os.path.join(self.projectPath, 'bin', baseExecutableName)
            
        shutil.copy2(executablePath, destExecutablePath)
        
        fi = open(os.path.join(utils.PATH_RES, 'templates', 'wrap', 'main.py'), 'rt')
        templateString = fi.read()
        fi.close()
        
        template = string.Template(templateString)
        newContent = template.safe_substitute(executableName=baseExecutableName)
        
        wrappedMainPath = os.path.join(self.projectPath, 'bin', 'main.py')
        
        fo = open(wrappedMainPath, 'wt')
        fo.write(newContent)
        fo.close()
        
        os.chmod(wrappedMainPath, 0o775)

#=============================================================================

def getLiftOfExistingProjects():
    
    ''' This should prevent creating an existing project. '''
    
    TOOLS_PATH = '/data/fem/+software/SKRIPTY/tools'
    IGNORE_PATHS = [
        '/data/fem/+software/SKRIPTY/tools/repos',
        '/data/fem/+software/SKRIPTY/tools/bin']
    ADD_PATHS = [
        '/data/fem/+software/SKRIPTY/tools/python/ansaTools',
        '/data/fem/+software/SKRIPTY/tools/python/metaTools']

    tools = {}
    toolPaths = ADD_PATHS
    for fileName in os.listdir(TOOLS_PATH):
        fileName = os.path.join(TOOLS_PATH, fileName)
        if os.path.isdir(fileName) and fileName not in IGNORE_PATHS:
            toolPaths.append(fileName)
    
    for toolPath in toolPaths:
        for toolName in os.listdir(toolPath):
            currentToolPath = os.path.join(toolPath, toolName)
            if os.path.isdir(currentToolPath):
                tools[toolName] = currentToolPath
                
    return tools
    
#=============================================================================

def main():
    
    parser = argparse.ArgumentParser(description=__doc__[:__doc__.find('Usage')],
    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('projectName', help='Project name.')
    parser.add_argument('path', nargs='?', metavar='project_path', #type=int, default=1,
        help='New project location. (Default=Current directory)')
    parser.add_argument('-wrap', nargs=1, metavar='script_path',
        dest='scriptPath',
        help='Automatically wraps given executable script with a newPyProject of a given name. \
        This project can be directly installed using pyProjectInstaller.')
    parser.add_argument('-ansaCheck', action='store_true',
        help='Creates an ANSA check template. Please be aware that in order to use \
        pyProjectInstaller the new created check file name must contain a prefix: check_*.py')
    parser.add_argument('-ansaButton', action='store_true',
        help='Creates an ANSA user script button template. This project can be directly \
        added to ANSA using pyProjectInstaller.')
    parser.add_argument('-metaSession', action='store_true',
        help='Creates a META session template. This project can be directly \
        added to META using pyProjectInstaller.')
    
    
    args = parser.parse_args()
    
    # check new project name
    projectName = args.projectName
    listOfProjects = getLiftOfExistingProjects()
    if projectName in listOfProjects.keys():
        print('Given project already exists: "%s"' % listOfProjects[projectName])
        sys.exit()
    
    # check project path
    if args.path is not None:
        path = os.path.abspath(args.path)
    else:
        path = os.path.abspath(os.path.curdir)
    
    if not os.path.exists(path):
        print('Given path does not exist: "%s"' % path)
        sys.exit()
    
    app = ProjectCreator(projectName, path)
    
    # check executable to be wrapped
    executablePath = None
    if args.scriptPath is not None:
        executablePath = os.path.abspath(args.scriptPath[0])
        if not os.path.exists(executablePath):
            print('Given path does not exist: "%s"' % executablePath)
            sys.exit()
        elif not stat.S_IXUSR & os.stat(executablePath)[stat.ST_MODE]:
            print('Given file is not executable! Change its mode (E.g. chmod 775 filename).')
            sys.exit()
        else:
            app.wrapExecutable(executablePath)
            sys.exit()
    
    # create ansa check template
    if args.ansaCheck:
        if not projectName.startswith('check_'):
            app.projectName = 'check_%s' % projectName

        app.createAnsaCheck()
        sys.exit()
    elif args.ansaButton:
        app.createAnsaButton()
        sys.exit()
    elif args.metaSession:
        app.createMetaSession()
        sys.exit()
    
    # create a new python project
    app.createNewPyProject()
    
       
#=============================================================================

if __name__ == '__main__':
    main()
    