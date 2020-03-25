#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
doc
===

Tool that generates a IDIADA tool documentation overview using SPHINX.

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

#==============================================================================

APPLICATION_NAME = 'doc'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for IDIADA tools documentation generation.'

#==============================================================================

import os
import sys
import argparse

from domain import doc_items as di

#=============================================================================

def main():
    
    parser = argparse.ArgumentParser(description=__doc__[:__doc__.find('Usage')],
    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-init', action='store_true',
        help='Clones existing IDIADA tool documentation files from github master repository and sets remote origin.')
    parser.add_argument('-update', action='store_true',
        help='Creates documentation html content from source documentation files.')
    parser.add_argument('-sync', action='store_true',
        help='Synchonises source documentation files with the master repository.')
    
    args = parser.parse_args()
    
    # initiate documentation from github
    if args.init:
        di.ToolDocumentation.initiateFromGithub()
        
        documentation = di.ToolDocumentation()
        documentation.create()
        documentation.show()
    elif args.update:
        documentation = di.ToolDocumentation()
        documentation.create()
        documentation.show()
    elif args.sync:
        di.ToolDocumentation.synchronise()
        
        documentation = di.ToolDocumentation()
        documentation.create()
        documentation.show()
    else:
#         di.ToolDocumentation.show()
        
        # check for doc updates
        needsUpdate = di.ToolDocumentation.checkUpdated()
        if needsUpdate:
            documentation = di.ToolDocumentation()
            documentation.create()
            documentation.show()

       
#=============================================================================

if __name__ == '__main__':
    
    main()
    