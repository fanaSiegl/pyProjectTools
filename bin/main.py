#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
pyProjectInstaller
==================

Python script for pyProject installation. According to the given 
installation type (execulable script, ANSA button, META button) handles
all corresponding procedures:

* installs pyProject to the default project structure
* installs a default sphinx documentation based on main.py documentation string
* handles the git repository versions

Usage
-----

usage::

    pyProjectInstaller 

  
'''

#===============================================================================

APPLICATION_NAME = 'pyProjectInstaller'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'script for new python project installation.'

#===============================================================================

import os
import sys
import traceback
import getpass
import socket

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi
from domain import comp_items as ci
from presentation import base_widgets as bw
from presentation import comp_widgets as cw
from presentation import dialogs

#=============================================================================

def saveExecute(method, *args):
    
    def wrapper(*args):
        
        parentApplication = args[0]
        parentApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            method(*args)
        except Exception as e:
            traceback.print_exc()
            
            QtGui.QMessageBox.critical(
                parentApplication.mainWindow, '%s' % parentApplication.APPLICATION_NAME,
                str(e))
        
        parentApplication.restoreOverrideCursor()
        
    return wrapper

#=============================================================================

class PyProjectInstallerException(Exception): pass

#=============================================================================

class InstallerApplication(QtGui.QApplication):
    
    APPLICATION_NAME = 'newPyProject Installer'
    
    def __init__(self):
        
        super(InstallerApplication, self).__init__(sys.argv)
        
        self.revision, self.modifiedBy, self.lastModified = utils.getVersionInfo()
        self.userName = getpass.getuser()
        self.machine = socket.gethostname()
        self.installer = ci.Installer()
        
        self.workDir = os.getcwd()
        self.sourceMainPath = ''
        
        self.mainWindow = MainWindow(self)
        self.installerPages = self.mainWindow.centralWidget().installerPages
        
        self._setupConnections()
        
        self.mainWindow.show()
        
        self._checkGitConfig()
            
    #---------------------------------------------------------------------------
    @saveExecute
    def setupContent(self, sourceMainPath):
        
        self._setMainModule(sourceMainPath)
        self.installer.setMainModule(self.sourceMainPath)
        
        self.installerPages[cw.ExecConfigPageWidget.NAME].setupContent()
        self.installerPages[cw.DocumentationPageWidget.NAME].setupContent()
        self.installerPages[cw.VersionPageWidget.NAME].setupContent()
                                
    #---------------------------------------------------------------------------
    
    def _setMainModule(self, sourceMainPath):
        
        self.sourceMainPath = str(sourceMainPath)

        self.workDir = os.path.dirname(self.sourceMainPath)

    #--------------------------------------------------------------------------

    def _setupConnections(self):
        
        # setup content after main module set
        self.installerPages[cw.ExecConfigPageWidget.NAME].mainModuleSet.connect(self.setupContent)
        self.installerPages[cw.DocumentationPageWidget.NAME].previewButton.clicked.connect(
            lambda: self.showDocumentationPreview())
        
        self.mainWindow.centralWidget().pageContainerWidget.installReady.connect(
            self.runInstallation)
        
        self.mainWindow.centralWidget().closeButton.clicked.connect(self.closeAllWindows)
               
    #--------------------------------------------------------------------------
    
    def _checkGitConfig(self):
        
        userHome = os.path.expanduser("~")
        gitConfigPath = os.path.join(userHome, '.gitconfig')
        
        if os.path.exists(gitConfigPath):
            print('git config file found: "gitConfigPath"')
            return
        
        QtGui.QMessageBox.critical(
            self.mainWindow, '%s' % self.APPLICATION_NAME,
            'This is the first usage of git and it needs to be configured.\nPlease provide a basic user information.')
        
        userName = self.userName
        email = ''
        
        newUserName, ok = QtGui.QInputDialog.getText(self.mainWindow, 'git config',
            'Please provide your name for git setup (name surname).')
        if ok:
            userName = newUserName
            
        newEmail, ok = QtGui.QInputDialog.getText(self.mainWindow, 'git config',
            'Please provide your email for git setup (name.surname@idiada.cz).')
        if ok:
            email = newEmail
        
        configString = '''[user]
    name = %s
    email = %s

[core]
    editor = kwrite''' % (userName, email)
        
        fo = open(gitConfigPath, 'wt')
        fo.write(configString)
        fo.close()
        
        QtGui.QMessageBox.information(
            self.mainWindow, '%s' % self.APPLICATION_NAME,
            'git config file created in:\n"%s"\n\n%s' % (gitConfigPath, configString))

    #--------------------------------------------------------------------------
    @saveExecute
    def showDocumentationPreview(self):
        
        # create temporary documentation
        self.dialog = dialogs.DocuPreviewDialog(self)
        self.dialog.show()
        
    #--------------------------------------------------------------------------
    @saveExecute
    def runInstallation(self):
        
        self.installer.install()
        
        self.restoreOverrideCursor()
        
        QtGui.QMessageBox.information(
            self.mainWindow, self.APPLICATION_NAME, 'Installation completed!')

#===============================================================================

class MainWindow(QtGui.QMainWindow):

    WIDTH = 600
    HEIGHT = 400

    STATUSBAR_MESSAGE_DURATION = 5000
    
    NEW_TOOL_GROUP_TEXT = '+ add a new group'
    
    def __init__(self, parentApplication):
        super(MainWindow, self).__init__()

        self.parentApplication = parentApplication
        self.permanentWidget = None
        
        self._setupWidgets()

        self._setWindowGeometry()
    
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        self.setWindowTitle('%s (%s)' % (
            self.parentApplication.APPLICATION_NAME, self.parentApplication.revision))
        
#         self.setWindowIcon(QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
        
        #self.setWindowState(QtCore.Qt.WindowMaximized)

    #--------------------------------------------------------------------------

    def _setupWidgets(self):
                
#         self.statusBar()
        
        self.setCentralWidget(cw.CentralWidget(self))
        
    #--------------------------------------------------------------------------

    def showStatusMessage(self, message):

        self.statusBar().showMessage(message, self.STATUSBAR_MESSAGE_DURATION)
      
    #--------------------------------------------------------------------------

    #def closeEvent(self, event):
        
        #self.parentApplication.saveSettings()
        
        #event.accept()

#=============================================================================

def main():

    app = InstallerApplication()    
    sys.exit(app.exec_())
    
#=============================================================================

if __name__ == '__main__':
    
    main()
