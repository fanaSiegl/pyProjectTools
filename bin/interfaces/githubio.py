#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import shutil
import subprocess
import errno
from string import Template
import tempfile

from domain import utils

#=============================================================================

HUB_EXECUTABLE = os.path.join(utils.PATH_BIN, 'interfaces', 'hub-linux-amd64-2.14.2', 'bin', 'hub')

CONTENT_CLONE = '''#!/usr/bin/bash

export GITHUB_USER="${userName}"
export GITHUB_PASSWORD="${password}"

touch ~/.netrc
echo "machine github.com" > ~/.netrc
echo "login" $GITHUB_USER >> ~/.netrc
echo "password" $GITHUB_PASSWORD >> ~/.netrc

git clone https://github.com/$GITHUB_USER/${projectName}.git

rm ~/.netrc
'''

CONTENT_CREATE = '''#!/usr/bin/bash

export GITHUB_USER="${userName}"
export GITHUB_PASSWORD="${password}"

touch ~/.netrc
echo "machine github.com" > ~/.netrc
echo "login" $GITHUB_USER >> ~/.netrc
echo "password" $GITHUB_PASSWORD >> ~/.netrc

hub create

git checkout master
git push origin master
git push --tags

rm ~/.netrc
'''

CONTENT_SYNC = '''#!/usr/bin/bash

export GITHUB_USER="${userName}"
export GITHUB_PASSWORD="${password}"

touch ~/.netrc
echo "machine github.com" > ~/.netrc
echo "login" $GITHUB_USER >> ~/.netrc
echo "password" $GITHUB_PASSWORD >> ~/.netrc

git checkout master
git push origin master
git push --tags

rm ~/.netrc
'''

#=============================================================================

class Githubio(object):
    
    githubSettings = utils.getGiuthubSettings()
    
    #---------------------------------------------------------------------------
    @classmethod
    def cloneProject(cls, projectName, targetPath=None):
        
        if targetPath is None:
            targetPath = tempfile.TemporaryDirectory().name
        
        templateString = Template(CONTENT_CLONE)
        content = templateString.safe_substitute(
            {'userName' : cls.githubSettings['GITHUB_USER'],
             'password' : cls.githubSettings['GITHUB_PASSWORD'],
             'projectName' : projectName})
        
        if not os.path.isdir(targetPath):
            os.makedirs(targetPath)
        
#         process = subprocess.Popen(
#             '', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
#             cwd=targetPath)
#         print(content.split('\n'))
#         for command in content.split('\n'):
#             command += '\n'
#             print(command)
#             try:
#                 process.stdin.write(command.encode('utf-8'))
#             except IOError as e:
#                 print(str(e))
#                 if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
#                     # Stop loop on "Invalid pipe" or "Invalid argument".
#                     # No sense in continuing with broken pipe.
#                     break
#                 else:
#                     # Raise any other error.
#                     raise
#         
#         process.stdin.close()
#         process.wait()
        
        cloneFileName = os.path.join(targetPath, 'cloneScript.script')
        fo = open(cloneFileName, 'wt')
        fo.write(content)
        fo.close()
        os.chmod(cloneFileName, 0o775)
         
        utils.runSubprocess('%s' % cloneFileName, targetPath)
        
        if os.path.isfile(cloneFileName):
            os.remove(cloneFileName)
        
        return targetPath
        
    #---------------------------------------------------------------------------
    @classmethod
    def createProject(cls, projectName, projectPath):
        
        templateString = Template(CONTENT_CREATE)
        content = templateString.safe_substitute(
            {'userName' : cls.githubSettings['GITHUB_USER'],
             'password' : cls.githubSettings['GITHUB_PASSWORD'],
             'projectName' : projectName})
        
        createFileName = os.path.join(projectPath, 'cloneScript.script')
        fo = open(createFileName, 'wt')
        fo.write(content)
        fo.close()
        os.chmod(createFileName, 0o775)
        
        utils.runSubprocess('%s' % createFileName, projectPath)
        
        os.remove(createFileName)
    
    #---------------------------------------------------------------------------
    @classmethod
    def pushProject(cls, projectName, projectPath):
        
        templateString = Template(CONTENT_SYNC)
        content = templateString.safe_substitute(
            {'userName' : cls.githubSettings['GITHUB_USER'],
             'password' : cls.githubSettings['GITHUB_PASSWORD'],
             'projectName' : projectName})
        
        createFileName = os.path.join(projectPath, 'syncScript.script')
        fo = open(createFileName, 'wt')
        fo.write(content)
        fo.close()
        os.chmod(createFileName, 0o775)
        
        utils.runSubprocess('%s' % createFileName, projectPath)
        
        os.remove(createFileName)
    
    #---------------------------------------------------------------------------
    @classmethod
    def syncProject(cls, projectPath):
        
        utils.runSubprocess('%s sync' % HUB_EXECUTABLE, projectPath)
        

            
#=============================================================================

    