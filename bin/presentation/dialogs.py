#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Python script for ...'''

import os
import sys
import re
import shutil

from PyQt4 import QtCore, QtGui
# from PyQt4 import QtWebKit

from domain import utils
from domain import base_items as bi
from presentation import base_widgets as bw

#===============================================================================

class DocuPreviewDialog(object):

    def __init__(self, parentApplication):

        self.parentApplication = parentApplication
        
    #---------------------------------------------------------------------------
    
    def show(self):
        
        docString = self.parentApplication.installer.procedureItems[bi.DocumetationItem.NAME].docString
        
        TEMPLATE = '''documentation preview
==========================

.. toctree::
   :maxdepth: 2
   
%s

   '''
        
        src = os.path.join(utils.PATH_RES, 'doc_preview')
        dst = os.path.join(utils.getInstallTypePaths()['INSTALLATION_PATHS_BASE']['DOCUMENTATON_PATH_TEMP'], 'sphinx')
        
        sourceSphinxPath = os.path.join(dst,'source')
        
        # initiate
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        
        shutil.copytree(src, dst)
                
        fo = open(os.path.join(sourceSphinxPath, 'index.rst'), 'wt')
        fo.write(TEMPLATE % docString)
        fo.close()
        
        command = 'sphinx-build -b html -d %s %s %s' % (
            os.path.join(dst, 'build', 'doctrees'),
            sourceSphinxPath, os.path.join(dst, 'build', 'html'))
        utils.runSubprocess(command)
                
        address = os.path.join(dst, 'build', 'html', 'index.html')   
        
        utils.runSubprocess('firefox %s &' % address)
    
#==============================================================================

class NewRevisionDialog(QtGui.QDialog):

    WIDTH = 320
    HEIGHT = 240
    
    TITLE = 'Manage new git revision'
    
    def __init__(self, parentApplication, tagName):
        super(NewRevisionDialog, self).__init__()
        
        self.parentApplication = parentApplication
        self.tagName = tagName
        
        self._setWindowGeometry()
        self._setupWidgets()
        self._setupConnections()
        
        self._setupProjectStatus()
        
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
        
#         self.setWindowModality(QtCore.Qt.ApplicationModal)
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
                
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
    #---------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
        
        self.layout().addWidget(QtGui.QLabel('Untracked files to be added:'))
        
        self.utrackedFilesListWidget = QtGui.QListWidget()
        self.layout().addWidget(self.utrackedFilesListWidget)
        
        self.layout().addWidget(QtGui.QLabel('Commit description'))
        
        self.commitMessageTextEdit = QtGui.QTextEdit()
        self.layout().addWidget(self.commitMessageTextEdit)
        
        # buttons
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout().addWidget(frame)
         
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        self.layout().addWidget(self.buttonBox)
    
    #---------------------------------------------------------------------------
    
    def _setupProjectStatus(self):
        
        stdout, stderr = utils.runSubprocess('git status',
            cwd=os.path.dirname(
            os.path.dirname(self.parentApplication.sourceMainPath)))
                
        untrackedFiles = list()
        untrackedBlock = False
        for line in stdout.splitlines():
            parts = line.split()
            if line.startswith('# Untracked files:'):
                untrackedBlock = True
                continue
            elif not line.startswith('#'):
                continue
            # skip empty line
            if len(parts) <= 1:
                continue
            elif line.startswith('#   (use "git add <file>'):
                continue
            if untrackedBlock:
                untrackedFiles.append(line.replace('#','').strip())
        
        for untrackedFile in untrackedFiles:
            self.utrackedFilesListWidget.addItem(
                bw.BaseListWidgetItem(self, untrackedFile))
    
    #---------------------------------------------------------------------------
    
    def accept(self):
                
        message = str(self.commitMessageTextEdit.toPlainText())
        
        if len(message) == 0:
            QtGui.QMessageBox.critical(self, '%s' % self.TITLE,
                'Please add commit description.')
            return
        
        for i in range(self.utrackedFilesListWidget.count()):
            item = self.utrackedFilesListWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                utils.runSubprocess('git add %s' % item.text(), cwd=os.path.dirname(
                    os.path.dirname(self.parentApplication.sourceMainPath)))
        
        # commit message
        utils.runSubprocess('git commit -a -m "%s"' % message, cwd=os.path.dirname(
            os.path.dirname(self.parentApplication.sourceMainPath)))        
        
        # add tag
        utils.runSubprocess('git tag %s' % self.tagName, cwd=os.path.dirname(
            os.path.dirname(self.parentApplication.sourceMainPath)))
        
        super(NewRevisionDialog, self).accept()
        
#==============================================================================

class InstallerCheckerReportDialog(QtGui.QDialog):

    WIDTH = 600
    HEIGHT = 240
    
    TITLE = 'Installer check'
    
    def __init__(self, parentApplication, report):
        super(InstallerCheckerReportDialog, self).__init__()
        
        self.parentApplication = parentApplication
        self.report = report
        
        self._setWindowGeometry()
        self._setupWidgets()
        self._setupConnections()
        
        self._setupContent()
        
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
                
        self.buttonBox.accepted.connect(self.accept)
        
    #---------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
                
        self.reportListWidget = QtGui.QListWidget()
        self.layout().addWidget(self.reportListWidget)
                
        # buttons
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout().addWidget(frame)
         
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        self.layout().addWidget(self.buttonBox)
    
    #---------------------------------------------------------------------------

    def _setupContent(self):
        
        for check in self.report:
            status, message = check
            item = QtGui.QListWidgetItem(message)
            if status == bi.BaseInstallItemChecker.CHECK_TYPE_OK:
                item.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogYesButton))
            elif status == bi.BaseInstallItemChecker.CHECK_TYPE_WARNING:
#                 item.setIcon(QtGui.QMessageBox.Warning)
                item.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning))
            elif status == bi.BaseInstallItemChecker.CHECK_TYPE_CRITICAL:
#                 item.setIcon(QtGui.QMessageBox.Critical)
                item.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MessageBoxCritical))
            self.reportListWidget.addItem(item)
            
