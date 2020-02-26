#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import configparser
import numpy as np
import subprocess

#==============================================================================

PATH_BIN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),'..'))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))
PATH_ICONS = os.path.join(PATH_RES, 'icons')

VERSION_FILE = 'version.ini'
CONFIG_FILE = 'config.ini'
USER_CONFIG_SETTINGS_FILE = 'user_settings.xml'

#==============================================================================

DFT_DOC_STRING = '''
Project name
============

Project function description.

Usage
-----

project_name [input parameter]

Description
-----------

* requires something
* does something
* creates something as an output

'''

#==============================================================================

def getVersionInfo():

    SECTION_VERSION = 'VERSION'
     
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, VERSION_FILE)
    config.read(cfgFileName)
         
    revision = config.get(SECTION_VERSION, 'REVISION')
    modifiedBy = config.get(SECTION_VERSION, 'AUTHOR')
    lastModified = config.get(SECTION_VERSION, 'MODIFIED')
 
    return revision, modifiedBy, lastModified

#==============================================================================

def getRemoteVersionInfo(pyProjectPath):

    SECTION_VERSION = 'VERSION'
    pathIni = os.path.normpath(os.path.join(
        pyProjectPath, '..', 'ini'))
    
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(pathIni, VERSION_FILE)
    config.read(cfgFileName)
         
    revision = config.get(SECTION_VERSION, 'REVISION')
    modifiedBy = config.get(SECTION_VERSION, 'AUTHOR')
    lastModified = config.get(SECTION_VERSION, 'MODIFIED')
 
    return revision, modifiedBy, lastModified

#===============================================================================

def registerClass(cls):
    cls.container[cls.NAME] = cls
    return cls

#==============================================================================

def runSubprocess(command, cwd=None):
    
    process = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        cwd=cwd)
    stdout, stderr = process.communicate()
    
    if stdout is not None:
        stdout = stdout.decode("ascii",errors="ignore")
    if stderr is not None:
        stderr = stderr.decode("ascii",errors="ignore")
    
    return stdout, stderr

#==============================================================================

def getInstallTypePaths():
         
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, CONFIG_FILE)
    config.read(cfgFileName)
    
    sections = dict()
    for sectionName in config.sections():
        sections[sectionName] = config[sectionName]
    
    return sections

#==============================================================================

def getEnvironmentExecutable(configFilePath):
         
    config = configparser.ConfigParser()
    
    try:
        cfgFileName = os.path.join(configFilePath, CONFIG_FILE)
        config.read(cfgFileName)
    
        return config['GENERAL']['EXECUTABLE']
    except Exception as e:
        return None
    
#==============================================================================
