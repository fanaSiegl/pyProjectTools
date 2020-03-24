#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
pyProjectTools
==============

Is a package of tools which are supposed to be used to create, install and document python-based scripts.
    
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

    doc [-h] [-init]

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

from domain import utils

import doc
import newPyProject
import pyProjectInstaller

#=============================================================================

class PyProjectTools(object):
    
    '''
pyProjectTools
==============

Description ...
    
    '''
    
    APPLICATION_NAME = 'pyProjectTools'
    
    def __init__(self):
        
        os.system('%s %s &' % (
            utils.getDocumentationBrowser(),
            os.path.join(utils.PATH_DOC, 'documentation.html')))
        
        revision, modifiedBy, lastModified = utils.getVersionInfo()
        
        print('%s (%s)' % (self.APPLICATION_NAME, revision))
        print('MODIFIED BY: %s' % modifiedBy)
        print('LAST MODIFIED: %s' % lastModified)
        
        print(PyProjectTools.__doc__)
       
        print(newPyProject.__doc__)
        print(pyProjectInstaller.__doc__)
        print(doc.__doc__)
            
#=============================================================================

if __name__ == '__main__':
    
    PyProjectTools()
