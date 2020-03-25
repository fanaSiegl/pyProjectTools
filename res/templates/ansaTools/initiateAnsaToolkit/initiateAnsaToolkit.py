#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for ANSA user script buttons configuration.

Note: ANSA requires a restart to load user button toolkit.
'''
  
import os
import sys
import argparse
import shutil

#=============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ANSA_TOOLKIT_PATH = os.path.normpath(os.path.join(PATH_SELF, '..', '..', 'ansa_toolkit', 'default'))

ANSA_LOCAL_HOME = os.path.join('.BETA','ANSA')
ANSA_VERSION = 'version_'
SOURCE_PATH = os.path.join(PATH_SELF, 'user_home_links')

#ANSA_TOOLKIT_LINK = 'ansa_toolkit'
ANSA_TRANSL = 'ANSA_TRANSL.py'
ANSA_VERSION_TRANSL = os.path.join(SOURCE_PATH, 'copy_2_each_ansa_version', 'ANSA_TRANSL.py')
USER_TOOLKIT = 'user_toolkit'

#=============================================================================

def copyFile(src, dst, force):
    
  if os.path.exists(dst) and not force:
    print 'File already exists: "%s"' % dst
    return
  if os.path.islink(dst) and not force:
    print 'File already exists: "%s"' % dst
    return
  elif os.path.exists(dst) and force:
    print 'Deleting existing file: "%s"' % dst
    os.remove(dst)
  elif os.path.islink(dst) and force:
    print 'Deleting existing file: "%s"' % dst
    os.unlink(dst)
  
  try:
    print 'Copying: "%s" to "%s"' % (src, dst)
    if os.path.islink(src):
        linkto = os.readlink(src)
        os.symlink(linkto, dst)
    else:
        shutil.copy(src, dst)
  except Exception as e:
    print str(e)

#=============================================================================

def copyDir(src, dst, force=False):
    
  if os.path.exists(dst) and not force:
    print 'File already exists: "%s"' % dst
    return
  elif os.path.exists(dst) and force:
    print 'Deleting existing file: "%s"' % dst
    os.remove(dst)
  
  try:
    print 'Copying: "%s" to "%s"' % (src, dst)
    shutil.copytree(src, dst)
  except Exception as e:
    print str(e)

#=============================================================================

def main(args):
  
    force = args.force
  
    userHomePath = os.path.os.path.expanduser('~')
    ansaLocalHome = os.path.join(userHomePath, ANSA_LOCAL_HOME)
    
    if not os.path.exists(ansaLocalHome):
      print 'No ANSA home found: %s does not exist' % ansaLocalHome
      print 'Run ANSA first then rerun this script.'
      return
      
    print 'Creating a local ANSA user script structure in "%s"' % ansaLocalHome

    ansaVersions = list()
    for fileName in os.listdir(ansaLocalHome):
      if fileName.startswith(ANSA_VERSION):
	ansaVersions.append(fileName)

    # copy links
    for version in ansaVersions:
      src = os.path.join(SOURCE_PATH, ANSA_VERSION_TRANSL)
      dst = os.path.join(ansaLocalHome, version, ANSA_TRANSL)
      
      copyFile(src, dst, force)

    # copy ANSA_TRANSL
    src = os.path.join(ANSA_TOOLKIT_PATH, ANSA_TRANSL)
    dst = os.path.join(ansaLocalHome, ANSA_TRANSL)
    if os.path.islink(dst) and not force:
        print 'File already exists: "%s"' % dst
    elif os.path.islink(dst) and force:
        print 'Deleting existing file: "%s"' % dst
        os.unlink(dst)
        os.symlink(src, dst)
    else:
        print 'Copying: "%s" to "%s"' % (src, dst)
        os.symlink(src, dst)

#    # copy toolkit link
#    copyFile(os.path.join(SOURCE_PATH, ANSA_TOOLKIT_LINK), os.path.join(ansaLocalHome, ANSA_TOOLKIT_LINK), force)
    
    # copy user_toolkit if not present
    copyDir(
        os.path.join(SOURCE_PATH, USER_TOOLKIT),
        os.path.join(ansaLocalHome, USER_TOOLKIT))

#=============================================================================

if __name__ == '__main__':
  
    parser = argparse.ArgumentParser(
	description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-f', dest='force', help='Overwrites existing files.', action='store_true')


    args = parser.parse_args()
    
    main(args)