#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Project name
============

Project function description.

Usage
-----

usage::

    project_name [input parameter]

Description
-----------

* does requires something
* does something
* creates something as an output

'''

#=========================== to be modified ===================================

APPLICATION_NAME = 'project_name'
DOCUMENTATON_GROUP = 'tool documentation group'
DOCUMENTATON_DESCRIPTION = 'Python application one line description.'

#==============================================================================

import os
import sys

#==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))
EXECUTABLE_NAME = '$executableName'

#==============================================================================

def main():
        
    arguments = sys.argv[1:]
    
    scriptPath = os.path.join(PATH_SELF, EXECUTABLE_NAME)
    
    os.system('%s %s' % (scriptPath, ' '.join(arguments)))
    
       
#==============================================================================

if __name__ == '__main__':
    main()
    