#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob

TOOL_PREFIX = 'tool_*.py'

path = os.path.dirname(os.path.realpath(__file__))

__all__ = list()
for filename in glob.glob(os.path.join(path, TOOL_PREFIX)):
		moduleName = os.path.basename(os.path.splitext(filename)[0])
		__all__.append(moduleName)



