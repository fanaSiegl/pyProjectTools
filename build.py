#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import shutil
import string
import subprocess
import argparse


PATH_SELF = os.path.dirname(os.path.realpath(__file__))

PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/bin'

VERSION_FILE = 'ini/version.ini'

EXECUTABLE = 'bin/installer.py'
APPLICATION_NAME = 'pyProjectInstaller'

DOCUMENTATON_PATH = '/data/fem/+software/SKRIPTY/tools/python/tool_documentation/default'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for new python project installation.'

#==============================================================================

def runSubprocess(command):
    
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    return process.communicate()


#==============================================================================

def createVersionFile():
    
    print 'Updating a version file'
    
    VERSION_FILE_TEMPLATE = '''[VERSION]
REVISION = ${revision}
AUTHOR = ${modifiedBy}
MODIFIED = ${lastModified}'''
    
    template = string.Template(VERSION_FILE_TEMPLATE)
    
    outputString = template.substitute(
        {'revision' : args.revision,
         'modifiedBy' : modifiedBy,
         'lastModified': lastModified})
    
    versionFile = open(os.path.join(targetDir, VERSION_FILE), 'wt')
    versionFile.write(outputString)
    versionFile.close()
    
#==============================================================================

def createRevisionContents():
    
    print 'Creating a revision content'
    
    if os.path.isdir(targetDir):
        print 'Current revision exists already.'
        sys.exit()
    else:
        os.makedirs(targetDir)
    
    runSubprocess('git clone . %s' % (targetDir))
    runSubprocess('git checkout %s' % (args.revision))

#==============================================================================

def cleanUp():
    
    print 'Cleaning up files'
    
    repositoryPath = os.path.join(targetDir, '.git')
    shutil.rmtree(repositoryPath)
        
    buildScript = os.path.join(targetDir, 'build.py')
    os.remove(buildScript)

    
#==============================================================================

def getRevisionInfo():
    
    print 'Gathering revision information'
    
    output, _ = runSubprocess('git log %s -n 1' % args.revision)
    
    lines = output.split('\n')
    
    modifiedBy = lines[1].split(':')[1].strip()
    lastModified = ':'.join(lines[2].split(':')[1:]).strip()
    
    return modifiedBy, lastModified

#==============================================================================

def install():
    
    print 'Releasing to the productive version'
    
    defaultDir = os.path.join(args.target, 'default')
    
    if os.path.islink(defaultDir):
        os.unlink(defaultDir)
    os.symlink(args.revision, defaultDir)
    
    symLink = os.path.join(PRODUCTIVE_VERSION_BIN, APPLICATION_NAME)
    executable = os.path.join(defaultDir, EXECUTABLE)
    if os.path.islink(symLink):
        os.unlink(symLink)
    os.symlink(executable, symLink)
    
    os.chmod(symLink, 0775)    

#==============================================================================

def createDocumentation():
    
    print 'Creating local sphinx documentation'
    
    SPHINX_DOC = os.path.join(targetDir, 'doc', 'sphinx')
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
    stdout, _ = runSubprocess('git log --graph --all --decorate --abbrev-commit')
    lines = stdout.splitlines()
        
    fo = open(GIT_REVISION_HISTORY, 'wt')
    fo.write(HEADER)
        
    for line in lines:
        fo.write('   %s\n' % line)
    fo.close()
    
    # create local documentation
    runSubprocess('python %s -b html -d %s %s %s' % (
        SPHINX_BUILD, SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))
    
#==============================================================================

def publishDocumentation():
    
    print 'Updating tool documentation'
    
    SPHINX_DOC = os.path.join(targetDir, 'doc', 'sphinx')
    SPHINX_HTML = os.path.join(SPHINX_DOC, 'build', 'html')
    
    SPHINX_INDEX = os.path.join(SPHINX_HTML, 'index.html')
    
    # copy to tool documentation
    docFileName = os.path.join(DOCUMENTATON_PATH, 'source',
        DOCUMENTATON_GROUP.replace(' ', '_'), '%s.rst' % APPLICATION_NAME)
    
    if not os.path.exists(os.path.dirname(docFileName)):
        os.mkdir(os.path.dirname(docFileName))
    
    if os.path.exists(docFileName):
        os.remove(docFileName)
    
    fo = open(docFileName, 'wt')
    fo.write('.. _%s: %s\n\n' % (APPLICATION_NAME, SPHINX_INDEX))
    fo.write('`%s`_ - %s\n\n' % (APPLICATION_NAME, DOCUMENTATON_DESCRIPTION))
    fo.close()
    
    # update tool documentation
    updateScriptPath = os.path.join(DOCUMENTATON_PATH, 'buildHtmlDoc.py')
    runSubprocess(updateScriptPath)
    

#==============================================================================
    
parser = argparse.ArgumentParser(description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('target', help='Build destination path.')
parser.add_argument('revision', help='Revision number to be build.')
parser.add_argument('-i', action='store_true',  dest='install',
    help='Makes a build revision default.')

args = parser.parse_args()

targetDir = os.path.join(args.target, args.revision)

createRevisionContents()
modifiedBy, lastModified = getRevisionInfo()
createVersionFile()
createDocumentation()
cleanUp()

if args.install:
    install()
    publishDocumentation()
    
print 'Done'