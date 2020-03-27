#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

from domain import utils

#==============================================================================

class AnsaChecksPlistUpdater(object):
    
    PLIST_GENERATOR_NAME = 'generate_plist.py'

    #--------------------------------------------------------------------------
    @classmethod
    def createPlist(cls):

        # create plist for available checks and the documentation string
        command = '%s -nogui -execscript %s' % (utils.getPathAnsaExecutable(),
            os.path.join(utils.PATH_BIN, 'interfaces', 'ansaChecksPlistUpdater',
            'bin', cls.PLIST_GENERATOR_NAME))
                        
        stdout, stderr = utils.runSubprocess(command)

        for line in stdout.splitlines():
            print(line)
        
        if stderr is not None:
            for line in stderr.splitlines():
                print(line)

#==============================================================================

# if __name__ == '__main__':
#     
#     AnsaChecksPlistUpdater.createPlist()