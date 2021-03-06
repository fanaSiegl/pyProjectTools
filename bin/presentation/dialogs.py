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
from domain import doc_items as di
from presentation import base_widgets as bw
from presentation import models

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
                
        srcConf = os.path.join(utils.PATH_RES, 'doc_preview', 'source', 'conf.py')
        dst = os.path.join(utils.getInstallTypePaths()['INSTALLATION_PATHS_BASE']['DOCUMENTATON_PATH_TEMP'], 'sphinx')
        
        sourceSphinxPath = os.path.join(dst, 'source')
        
        # initiate
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        
        # copy source files
        try:
            projectDocSouce = os.path.join(self.parentApplication.installer.pyProjectPath, 'doc', 'sphinx', 'source')
            shutil.copytree(projectDocSouce, sourceSphinxPath)
            
            # delete file which should be updated
            if os.path.isfile(os.path.join(sourceSphinxPath, 'conf.py')):
                os.remove(os.path.join(sourceSphinxPath, 'conf.py'))
#             if os.path.isfile(os.path.join(sourceSphinxPath, 'index.rst')):
#                 os.remove(os.path.join(sourceSphinxPath, 'index.rst'))
                
        except Exception as e:
            print('Failed to copy documentation source files! (%s)' % str(e))
        
#         if not os.path.isfile(os.path.join(sourceSphinxPath, 'conf.py')):
        shutil.copy(srcConf, os.path.join(sourceSphinxPath, 'conf.py'))
        
        if os.path.isfile(os.path.join(sourceSphinxPath, 'index.rst')):
            fi = open(os.path.join(sourceSphinxPath, 'index.rst'))
            TEMPLATE = fi.read().replace('.. automodule:: main', '%s') 
            fi.close()
            
        fo = open(os.path.join(sourceSphinxPath, 'index.rst'), 'wt')
        fo.write(TEMPLATE % docString)
        fo.close()
                
        # create local documentation using installer environment 
        envExecutable = utils.getEnvironmentExecutable(utils.PATH_INI)
        utils.runSubprocess('%s -b html -d %s %s %s' % (
            os.path.join(os.path.dirname(envExecutable), 'sphinx-build'),
            os.path.join(dst, 'build', 'doctrees'),
            sourceSphinxPath, os.path.join(dst, 'build', 'html')))
                        
        address = os.path.join(dst, 'build', 'html', 'index.html')   
        
        os.system('%s %s &' % (
            utils.getDocumentationBrowser(), address))
    
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
            

#==============================================================================

class MasterRepositorySelectionDialog(QtGui.QDialog):

    WIDTH = 1200
    HEIGHT = 800
    
    TITLE = 'IDIADA tools master repository'
    
    def __init__(self, parentApplication):
        super(MasterRepositorySelectionDialog, self).__init__()
        
        self.parentApplication = parentApplication
        self.installer = self.parentApplication.installer
        self.loadingThread = LoadMasterRepositoryProjectsThread(self)
        self.selectedItems = list()
        
        self._setWindowGeometry()
        self._setupWidgets()
        self._setupConnections()
        
        self.loadingThread.start()
                
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        self.setWindowTitle(self.TITLE)
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
                
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.helpRequested.connect(self._openDocumentation)
        
        self.loadingThread.dataLoaded.connect(self._setupContent)
                
    #---------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
                
        self.toolListTreeView = QtGui.QTreeView()
        self.layout().addWidget(self.toolListTreeView)
                
        # buttons
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout().addWidget(frame)
         
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.addButton('Open documentation', QtGui.QDialogButtonBox.HelpRole)

        self.layout().addWidget(self.buttonBox)
    
    #---------------------------------------------------------------------------

    def _setupContent(self, toolGroups):
        
        # setup available tools
        self.installer.setToolGroups(toolGroups)
        
        toolModel = models.BaseTreeModel(toolGroups)
        
        self.toolListTreeView.setModel(toolModel)
        
        self.toolListTreeView.expandAll()
        self.toolListTreeView.resizeColumnToContents(0)
    
    #---------------------------------------------------------------------------
    
    def _openDocumentation(self):
        
        di.ToolDocumentation.show()
    
    #---------------------------------------------------------------------------
    
    def accept(self):
        
        self.selectedItems = self.getSelectedItems()
        
        if len(self.selectedItems) == 0:            
            QtGui.QMessageBox.critical(
                self, self.TITLE, 'No project selected!')
        else:
            answer = QtGui.QMessageBox.question(
                self, self.TITLE,
                'Are you sure to download this tool from master repository?',
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                return
            
            super(MasterRepositorySelectionDialog, self).accept()
    
    #--------------------------------------------------------------------------

    def getSelectedItems(self):
         
        selectedItems = list()
        for index in self.toolListTreeView.selectedIndexes():
            item = index.model().itemFromIndex(index)
            if index.column() > 0:
                continue
            if hasattr(item, 'dataItem') and item.dataItem is not None:
                selectedItems.append(item.dataItem)
        
        return selectedItems


#==============================================================================

class LoadMasterRepositoryProjectsThread(QtCore.QThread):
    
    dataLoaded = QtCore.pyqtSignal(object)
    
    def __init__(self, parentDialog):
        super(LoadMasterRepositoryProjectsThread, self).__init__()
        
        self.parentDialog = parentDialog 
        self.parentApplication = parentDialog.parentApplication
        
        self.started.connect(
            lambda: self.parentApplication.setOverrideCursor(
                QtGui.QCursor(QtCore.Qt.WaitCursor)))
        self.finished.connect(
            self.parentApplication.restoreOverrideCursor)
            
    #--------------------------------------------------------------------------
    
    def run(self):
                
        self.dataLoaded.emit(di.ToolDocumentation.getListOfTools())
        

#==============================================================================
        
                    