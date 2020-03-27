#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys    
import numpy as np
import subprocess

import configparser

#==============================================================================

PATH_BIN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),'..','..','..','..'))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))
PATH_ICONS = os.path.join(PATH_RES, 'icons')

CONFIG_FILE = 'config.ini'
VERSION_FILE = 'version.ini'

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

def getPlistPath():
     
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, CONFIG_FILE)
    config.read(cfgFileName)
 
    return config.get('INSTALLATION_PATHS_TYPE_ANSA_CHECK', 'CHECK_INSTALLER_PLIST_PATH')
    
#==============================================================================

def getPathChecks():
     
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, CONFIG_FILE)
    config.read(cfgFileName)
 
    return config.get('INSTALLATION_PATHS_TYPE_ANSA_CHECK', 'CHECK_INSTALLER_CHECKS_PATH')

#==============================================================================

def getPathChecksRepos():
     
    config = configparser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, CONFIG_FILE)
    config.read(cfgFileName)
 
    return config.get('INSTALLATION_PATHS_TYPE_ANSA_CHECK', 'REPOS_PATH')


#==============================================================================
