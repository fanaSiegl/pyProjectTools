#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
#from importlib import import_module

TOOL_PREFIX = 'tool_*'

PATH_SELF = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PATH_SELF)

__all__ = list()
modules = list()
for filename in glob.glob(os.path.join(PATH_SELF, TOOL_PREFIX)):
    moduleName = os.path.basename(os.path.splitext(filename)[0])
    __all__.append(moduleName)
    #modules.append(import_module(moduleName))

