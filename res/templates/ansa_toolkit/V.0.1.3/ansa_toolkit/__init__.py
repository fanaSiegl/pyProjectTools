#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob

import ansa

PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ANSA_LOCAL_HOME = os.path.join('.BETA','ANSA')

userHomePath = os.path.os.path.expanduser('~')
ansaLocalHome = os.path.join(userHomePath, ANSA_LOCAL_HOME)

sys.path.append(PATH_SELF)
sys.path.append(ansaLocalHome)

# import tools
#import beta_scripts
#from python_scripts import *
#from other_python_scripts import *

TOOL_PREFIX = 'tool_*'

for modulePath in glob.glob(os.path.join(PATH_SELF, 'python_scripts', TOOL_PREFIX)):
    print(modulePath)
    ansa.ImportCode(modulePath)

# import user scripts
try:
    from user_toolkit import *
except Exception as e:
    print('User scripts not found.')