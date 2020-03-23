#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
tool documentation
==================

Tool that generates a IDIADA tool documentation overview using SPHINX

Usage
-----

| doc           -> opens the IDIADA tools documentation in a browser
| doc-update    -> updates the IDIADA tools documentation

'''

#==============================================================================

APPLICATION_NAME = 'doc-update'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for IDIADA tools documentation generation.'

#==============================================================================

import os
import sys

from domain import doc_items as di

#=============================================================================

def main():
    
    di.ToolDocumentation.show()
     
    needsUpdate = di.ToolDocumentation.checkUpdated()
    if needsUpdate:
        documentation = di.ToolDocumentation()
        documentation.create()
        documentation.show()
#     else:
#         ToolDocumentation.show()
     
    return
    documentation = di.ToolDocumentation()
    toolGroups = documentation.getListOfTools()
             
    for groupName in sorted(toolGroups.keys()):            
         
        print(groupName)
        tools = toolGroups[groupName]
        for tool in tools:
            print(tool.isLocal(), tool.name, tool.version(), tool.getOneLineDescription())
        
    return
    documentation = di.ToolDocumentation()
    documentation.create()
    
    print("Build finished.")
       
#=============================================================================

if __name__ == '__main__':
    
    main()
    