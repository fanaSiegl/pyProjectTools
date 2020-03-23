#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Project name
============

Project function description.

* does requires something
* does something
* creates something as an output

Usage
-----

usage::

    project_name [input parameter]

example::

    project_name "input parameter"

Remarks
-------

.. warning::
    
    Requires something
    
* requires something
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

from domain import utils

#==============================================================================
    
class Project(object):
    
    APPLICATION_NAME = 'New project name'
    
    def __init__(self, args):
        
        print(self.APPLICATION_NAME) 
        
        self.method1()
        
    #--------------------------------------------------------------------------

    def method1(self):
        
        print(utils.getVersionInfo())


#==============================================================================

def main():
        
    project = Project(sys.argv)
    
       
#==============================================================================

if __name__ == '__main__':
    main()
    