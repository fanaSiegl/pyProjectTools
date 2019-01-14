#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import imp
import tempfile

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi
import dialogs
import base_widgets as bw

#===============================================================================

INSTALLER_PAGE_TYPES = dict()

#===============================================================================

class ModuleFileNameException(Exception): pass

#===============================================================================

class RevisionException(Exception): pass

#===============================================================================

class CentralWidget(QtGui.QWidget):
    
    def __init__(self, mainWindow):
        super(CentralWidget, self).__init__()
        
        self.mainWindow = mainWindow 
        self.parentApplication = mainWindow.parentApplication
        
        self.installerPages = dict()
        
        self._setupWidgets()
        self._setupConnections()
        
        self._checkButtonStates()
    
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
                        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        upperPaneLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(upperPaneLayout)
        
        self.pageListLayout = QtGui.QVBoxLayout()
        upperPaneLayout.addLayout(self.pageListLayout)
        
        # add separator
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.VLine)
        upperPaneLayout.addWidget(frame)
        
        # setup pages
        self.pageContainerWidget = PageContainerWidget(self)#QtGui.QStackedWidget()
        
        upperPaneLayout.addWidget(self.pageContainerWidget)
                
        self.pageListLayout.addStretch()

        # buttons
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout.addWidget(frame)
        
        self.buttonBox = QtGui.QDialogButtonBox()
#         self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        
#         self.installButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        self.closeButton = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        
        
        self.backButton = QtGui.QPushButton('< Back')
        self.buttonBox.layout().insertWidget(1, self.backButton)
        self.nextButton = QtGui.QPushButton('Next >')
        self.buttonBox.layout().insertWidget(2, self.nextButton)
                
        # setup user info
        userInfo = QtGui.QLabel('Current user: %s@%s' % (
        self.parentApplication.userName, self.parentApplication.machine))
        
        self.buttonBox.layout().insertWidget(0, userInfo)
        
        self.layout.addWidget(self.buttonBox)
    
    #--------------------------------------------------------------------------

    def _setupConnections(self):
    
        self.backButton.clicked.connect(self.pageContainerWidget.back)
        self.nextButton.clicked.connect(self.pageContainerWidget.next)
        
        self.pageContainerWidget.currentChanged.connect(self._checkButtonStates)
        
        # connect next button behavior
        for pageWidget in self.installerPages.values():
#             pageWidget.hasFinished.connect(lambda:self.nextButton.setEnabled(True))
            pageWidget.hasFinished.connect(self._checkButtonStates)
        
    #--------------------------------------------------------------------------

    def _checkButtonStates(self):
        
        self.backButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        
        currentIndex = self.pageContainerWidget.currentIndex()
        currentWidget = self.pageContainerWidget.currentWidget()
        if currentIndex == 0:
            self.backButton.setEnabled(False)
        else:
            self.backButton.setEnabled(True)
        
        if currentWidget.finished:
            self.nextButton.setEnabled(True)
#         else:
#             self.nextButton.setEnabled(False)
        
#         if currentIndex == len(self.installerPages) - 1:
        if type(currentWidget) is VersionPageWidget:
            self.nextButton.setText('Install')
        else:
            self.nextButton.setText('Next >')
        
    #--------------------------------------------------------------------------

    def registerPage(self, pageWidget):
        
#         self.installerPages.append(pageWidget)
        self.installerPages[pageWidget.NAME] = pageWidget
    
                    
#==============================================================================

class PageContainerWidget(QtGui.QStackedWidget):
    
    installReady = QtCore.pyqtSignal()
    
    def __init__(self, centralWidget):
        super(PageContainerWidget, self).__init__()
        
        self.centralWidget = centralWidget
        self.mainWindow = centralWidget.mainWindow
        self.parentApplication = self.mainWindow.parentApplication
        
        self.pages = dict()
        
        self._setupWidgets()
        self._setupConnections()
        
        # activate first page
#         self.setCurrentIndex(0)
        self.widget(0).setActivated(True)
            
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        # setup pages
        for pageWidget in INSTALLER_PAGE_TYPES.values():
            self.pages[pageWidget.PAGE_NO] = pageWidget(self)
            
        for pageWidgetIndex in sorted(self.pages.keys()):
            currentWidget = self.pages[pageWidgetIndex]
            
            self.centralWidget.pageListLayout.addWidget(currentWidget.pageNameLabel)
            self.addWidget(currentWidget)
            
            self.centralWidget.registerPage(currentWidget)
                
    #--------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.currentChanged.connect(self._setActivePage)
            
    #--------------------------------------------------------------------------
    
    def _setActivePage(self):
        
#         for pageWidgetIndex in range(self.count()):
#             self.widget(pageWidgetIndex).deactivated.emit()
                
        self.currentWidget().activated.emit()
    
    #--------------------------------------------------------------------------
    
    def next(self):

        try:
            self.widget(self.currentIndex())._checkContent()
        except bi.InstallerCheckerException as e:
            return

#TODO: make up something more elegant 
        # run installation
        if self.currentIndex() == self.count() - 1:
            # this will perform checks
            self.widget(self.currentIndex()).deactivated.emit()
            # run installation if everything is ok
            self.installReady.emit()
            # this keeps label bolt
            self.widget(self.currentIndex()).setActivated(True)
        else:            
            self.widget(self.currentIndex()).deactivated.emit()
            self.setCurrentIndex(self.currentIndex() + 1)
                    
    #--------------------------------------------------------------------------
    
    def back(self):
        
        self.widget(self.currentIndex()).setActivated(False)
        
        self.setCurrentIndex(self.currentIndex() - 1)
    
    
    
#==============================================================================

class BaseInstallerPageWidget(bw.BaseItemParamSyncWidget):
    
    container = INSTALLER_PAGE_TYPES
    NAME = ''
    DESCRIPTION = ''
    PAGE_NO = -1
    
    activated = QtCore.pyqtSignal()
    deactivated = QtCore.pyqtSignal()
    hasFinished = QtCore.pyqtSignal()
        
    def __init__(self, centralWidget):
        super(BaseInstallerPageWidget, self).__init__()
        
        self.centralWidget = centralWidget
        self.mainWindow = centralWidget.mainWindow
        self.parentApplication = self.mainWindow.parentApplication 
        self.installer = self.parentApplication.installer
        
        self.installationItem = self.installer.procedureItems[
            self.NAME]
#             bi.INSTALLER_PROCEDURE_ITEMS[]()
        
        self.finished = False
        
        self._setupCommonWidgets()
        self._initiateContent()
        self._setupCommonConnections()
        
    #--------------------------------------------------------------------------

    def _setupCommonWidgets(self):
        
        self.pageNameLabel = QtGui.QLabel(self.NAME)
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        descriptionLabel = QtGui.QLabel(self.DESCRIPTION)
        font = QtGui.QFont()
        font.setBold(True)
        descriptionLabel.setFont(font)
        
        self.layout.addWidget(descriptionLabel)
        
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout.addWidget(frame)
        
        self._setupWidgets()
        
        self.layout.addStretch()
                
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        pass

    #--------------------------------------------------------------------------
    
    def _initiateContent(self):
        
        pass

    #--------------------------------------------------------------------------
    
    def _checkContent(self):
                
        status, result = self.installationItem.check()
        
        if status != bi.BaseInstallItemChecker.CHECK_TYPE_OK:
            reportDialog = dialogs.InstallerCheckerReportDialog(
                self.parentApplication, result)
            reportDialog.exec_()
            
            raise bi.InstallerCheckerException()

    #--------------------------------------------------------------------------

    def _setupCommonConnections(self):

        self.activated.connect(lambda: self.setActivated(True))
        
#         self.deactivated.connect(self._checkContent)
        self.deactivated.connect(lambda: self.setActivated(False))
        
        self.hasFinished.connect(lambda: setattr(self, 'finished', True))
        
        self._setupConnections()
        
    #--------------------------------------------------------------------------

    def _setupConnections(self):
        
        pass
    
    #--------------------------------------------------------------------------

    def setActivated(self, value):
        
        font = QtGui.QFont()
        font.setBold(value)
        self.pageNameLabel.setFont(font)
    
    #--------------------------------------------------------------------------

    
        

#==============================================================================
@utils.registerClass
class ExecConfigPageWidget(BaseInstallerPageWidget):
    
    NAME = bi.InstallationSetupItem.NAME
    DESCRIPTION = 'Select the installation type and a name of the executable.'
    PAGE_NO = 0
    
    mainModuleSet = QtCore.pyqtSignal(str)
    
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.execConfigWidgets = dict()
        
        # source project
        groupSource = QtGui.QGroupBox('Source pyProject')
        groupSource.setLayout(QtGui.QVBoxLayout())
        self.layout.addWidget(groupSource)
         
        # install type
        self.installTypeComboBox = QtGui.QComboBox()
         
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('Install type'))
        layout.addWidget(self.installTypeComboBox)
        groupSource.layout().addLayout(layout)
         
        # source file 
        self.sourcePyProjectLineEdit = QtGui.QLineEdit()
        self.browseButton = QtGui.QPushButton('Browse')
         
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('Source pyProject'))
        layout.addWidget(self.sourcePyProjectLineEdit)
        layout.addWidget(self.browseButton)
        groupSource.layout().addLayout(layout)
        
        # project name
        self.sourcePyProjectNameLineEdit = QtGui.QLineEdit()
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel('pyProject name'))
        layout.addWidget(self.sourcePyProjectNameLineEdit)
        self.sourcePyProjectNameLineEdit.setEnabled(False)
        groupSource.layout().addLayout(layout)
        
        # execution
        groupExec = QtGui.QGroupBox('Execution settings')
        groupExec.setLayout(QtGui.QVBoxLayout())
        self.layout.addWidget(groupExec)
         
        self.executableStackedWidget = QtGui.QStackedWidget()
         
        groupExec.layout().addWidget(self.executableStackedWidget)
         
         
        for execConfigWidget in bw.INSTALL_CONFIG_WIDGETS.values():
            currentWidget = execConfigWidget(self)
             
            self.executableStackedWidget.addWidget(currentWidget)
             
            # register added widget for easier switching
            self.execConfigWidgets[
                currentWidget.NAME] = self.executableStackedWidget.indexOf(currentWidget)

    #--------------------------------------------------------------------------
    
    def _initiateContent(self):
        
        self.installTypeComboBox.addItems(bi.INSTALL_TYPES.keys())
        
        # initiate install type
        execConfigType = self.executableStackedWidget.currentWidget()
        self._setInstallationType(execConfigType.installationItem)

    #--------------------------------------------------------------------------

    def _setupConnections(self):
                
#         self.sourcePyProjectLineEdit.textChanged.connect(self._checkMainModuleFileName)
        self.installTypeComboBox.currentIndexChanged.connect(
            self._installTypeChanged)
        self.browseButton.clicked.connect(self._selectSourcePyProject)
        
        self._connectLineEditWidget(self.sourcePyProjectNameLineEdit, 'projectName')
                
    #--------------------------------------------------------------------------
    
    def _installTypeChanged(self):
                
        # set config widget
        currentInstallTypeName = str(self.installTypeComboBox.currentText()) 
        execConfigIndex = self.execConfigWidgets[currentInstallTypeName]
        self.executableStackedWidget.setCurrentIndex(execConfigIndex)
        
        execConfigType = self.executableStackedWidget.currentWidget()
        
        self._setInstallationType(execConfigType.installationItem)
    
    #--------------------------------------------------------------------------

    def _setInstallationType(self, installTypeItem):
        
#         self.parentApplication.installer.setInstallationType(installTypeItem)
        self.installationItem.installTypeItem = installTypeItem
        
    #--------------------------------------------------------------------------
    
    def _selectSourcePyProject(self):
        
        installationItem = self.executableStackedWidget.currentWidget().installationItem
        
        fileName = QtGui.QFileDialog.getOpenFileName(self.mainWindow,
            'Select pyProject source', self.parentApplication.workDir,
            filter = installationItem.SOURCE_FILE_FILTER)
         
        if not fileName:
            return
        
        fileName = str(fileName)
        
        self._checkMainModuleFileName(fileName)
        
        self.sourcePyProjectLineEdit.setText(fileName)
        
        self._loadMainModule(fileName)
        self._setupPyProjectName(fileName)
    
    #--------------------------------------------------------------------------
    
    def _setupPyProjectName(self, fileName):
        
        ''' Set project name automatically based on installation type '''
        
        installationItem = self.executableStackedWidget.currentWidget().installationItem
        
        self.sourcePyProjectNameLineEdit.setText(
            installationItem.getProjectNameFromSourceFile(fileName))
        
    #--------------------------------------------------------------------------
    
    def _checkMainModuleFileName(self, sourceMainPath):
                
        if len(sourceMainPath) == 0:
            raise ModuleFileNameException('Given file not given!')
        
        if not os.path.exists(sourceMainPath):
            raise ModuleFileNameException('Given file does not exit!')
#         elif os.path.basename(sourceMainPath) != 'main.py':
#             raise ModuleFileNameException('Given file must be a pyProject generated creator.py!')
        
        self.hasFinished.emit()
    
    #--------------------------------------------------------------------------
    
    def _loadMainModule(self, sourceMainPath):
        
        ''' Name for the new loaded module must always be unique. Otherwise
        there are issues obtaining the doc string properly.'''
        
#         
#         tmpFile = tempfile.NamedTemporaryFile()
#         
#         mainModule = imp.load_source(tmpFile.name, str(sourceMainPath))
#         
#         self.mainModuleSet.emit(mainModule)
        
        self.mainModuleSet.emit(sourceMainPath)
                
    #--------------------------------------------------------------------------
    
    def setupContent(self):
        
        for execConfigWidgetNo in self.execConfigWidgets.values():
            
            execConfigWidget = self.executableStackedWidget.widget(execConfigWidgetNo)
            execConfigWidget.setExecSettingsFromMainModule()
        
                  
#==============================================================================
@utils.registerClass
class DocumentationPageWidget(BaseInstallerPageWidget):
    
    NAME = bi.DocumetationItem.NAME
    DESCRIPTION = 'Fill in information for the script documentation.'
    PAGE_NO = 1

    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        # documentation
        groupDoc = QtGui.QGroupBox('Documentation')
        groupDoc.setLayout(QtGui.QVBoxLayout())
        self.layout.addWidget(groupDoc)
         
        layout = QtGui.QGridLayout()
        groupDoc.layout().addLayout(layout)
         
        # documentation group
        self.docuGroupCombobox = bw.DocumentationGroupComboBox(self)
          
        layout.addWidget(QtGui.QLabel('Tool group'), 0, 0)
        layout.addWidget(self.docuGroupCombobox, 0, 1)
         
        # documentation description
        self.docuDescription = QtGui.QLineEdit()
         
        layout.addWidget(QtGui.QLabel('Tool description'), 1, 0)
        layout.addWidget(self.docuDescription, 1, 1)
         
        # documentation string
        groupDoc.layout().addWidget(QtGui.QLabel('Tool detailed description'))
        
        self.documentationTextEdit = QtGui.QTextEdit()
        self.documentationTextEdit.setReadOnly(True)
         
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.documentationTextEdit.setFont(font)
         
        groupDoc.layout().addWidget(self.documentationTextEdit)
         
        layout = QtGui.QHBoxLayout()
        layout.addStretch()
         
        # enable editing
        self.editDocStringButton = QtGui.QPushButton('Edit')
                 
        layout.addWidget(self.editDocStringButton)
         
        # default documentation string
        self.dftDocStringButton = QtGui.QPushButton('Default doc')
        self.dftDocStringButton.setEnabled(False)
         
        layout.addWidget(self.dftDocStringButton)
         
        # preview
        self.previewButton = QtGui.QPushButton('Preview')
                 
        layout.addWidget(self.previewButton)
        groupDoc.layout().addLayout(layout)

    #--------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.editDocStringButton.clicked.connect(self.enableDocStringEditing)
        self.dftDocStringButton.clicked.connect(self.setDftDocString)
        
        # connect parent item
        self._connectComboBoxWidget(self.docuGroupCombobox, 'docuGroup')
        self._connectLineEditWidget(self.docuDescription, 'docuDescription')
        self._connectTextEditWidget(self.documentationTextEdit, 'docString')
        
    #--------------------------------------------------------------------------

    def setupContent(self):
                
        self.docuGroupCombobox.addNewItem(
            self.installer.mainModuleItem.documentationGroup)
        
        self.docuDescription.clear()
        self.setDocuDescription(
            self.installer.mainModuleItem.documentationDescription)
        
        self.documentationTextEdit.clear()
        self.setDocString(self.installer.mainModuleItem.docString)
        
        # deactivate non relevant parameters 
        if self.installer.getCurrentInstallType() == bi.BaseInstallType.TYPE_ANSA_CHECK:
                         
            self.docuGroupCombobox.setEnabled(False)
            self.docuDescription.setEnabled(False)
        else:
            self.docuGroupCombobox.setEnabled(True)
            self.docuDescription.setEnabled(True)
        
        self.hasFinished.emit()

    #--------------------------------------------------------------------------

    def setDocuDescription(self, text):
        
        if len(text) > 0:
            self.docuDescription.clear()
            self.docuDescription.setText(text)
        
    #--------------------------------------------------------------------------

    def setDocString(self, text):
        
        if len(self.documentationTextEdit.toPlainText()) > 0:
            answer = QtGui.QMessageBox.question(
                self.mainWindow, '%s' % self.parentApplication.APPLICATION_NAME,
                'Current documentation string will be deleted. Do you want to continue?',
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                return
        
        self.documentationTextEdit.clear()
        self.documentationTextEdit.setText(text)
        
    #--------------------------------------------------------------------------
    
    def enableDocStringEditing(self):
        
        answer = QtGui.QMessageBox.question(
            self.mainWindow, '%s' % self.parentApplication.APPLICATION_NAME,
            'When you edit the documentation string you will have to create a new program version. \nDo you want to continue?',
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return
        
        self.documentationTextEdit.setReadOnly(False)
        self.dftDocStringButton.setEnabled(True)
    
    #--------------------------------------------------------------------------
    
    def setDftDocString(self):
        
        self.setDocString(utils.DFT_DOC_STRING)

        
#==============================================================================
@utils.registerClass
class VersionPageWidget(BaseInstallerPageWidget):
    
    NAME = bi.VersionItem.NAME
    DESCRIPTION = 'Select version for installation or create a new one.'
    PAGE_NO = 2
    
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
                 
        # installation
        groupInstall = QtGui.QGroupBox('Installation')
        groupInstall.setLayout(QtGui.QVBoxLayout())
        self.layout.addWidget(groupInstall)
         
        layout = QtGui.QGridLayout()
        groupInstall.layout().addLayout(layout)
                 
        # revision
        self.tagCombobox = bw.ProjectTagComboBox(self)
          
        layout.addWidget(QtGui.QLabel('Select version'), 0, 0)
        layout.addWidget(self.tagCombobox, 0, 1)
        
        # status overview
        self.layout.addWidget(QtGui.QLabel('Untracked files to be added:'))
        
        self.utrackedFilesListWidget = QtGui.QListWidget()
        self.layout.addWidget(self.utrackedFilesListWidget)
        
        self.layout.addWidget(QtGui.QLabel('Commit description'))
        
        self.commitMessageTextEdit = QtGui.QTextEdit()
        self.layout.addWidget(self.commitMessageTextEdit)

    #--------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.tagCombobox.currentIndexChanged.connect(self._setupCommitMessage)
        self.tagCombobox.itemAdded.connect(self._initialteNewCommitMessage)
        
        # connect parent item
        self._connectComboBoxWidget(self.tagCombobox, 'tagName')
        self._connectListWidget(self.utrackedFilesListWidget, 'filesToAdd')
        self._connectTextEditWidget(self.commitMessageTextEdit, 'commitMessage')
                
    #--------------------------------------------------------------------------
    
    def _setupTagList(self):
                
#         stdout, stderr = utils.runSubprocess('git tag -n9',
#             cwd=os.path.dirname(self.parentApplication.sourceMainPath))
#         
#         tagList = list()
#         for line in stdout.splitlines():
#             parts = line.strip().split()
#             tagList.append(parts[0])
        
        self.installationItem.setCurrentTagList(
            os.path.dirname(self.parentApplication.installer.mainModulePath))
        
        self.tagCombobox.setupTagList(self.installationItem.tagList)
    
    #---------------------------------------------------------------------------
    
    def _initialteNewCommitMessage(self):
        
        self.commitMessageTextEdit.clear()
        self.commitMessageTextEdit.setReadOnly(False)
    
    #---------------------------------------------------------------------------
    
    def _setupCommitMessage(self):
        
        message = self.installationItem.getTagCommitMessage(
            str(self.tagCombobox.currentText()))
        
        if len(message) > 0:
            self.commitMessageTextEdit.clear()
            self.commitMessageTextEdit.setText(message)
            self.commitMessageTextEdit.setReadOnly(True)
        else:
            self.commitMessageTextEdit.setReadOnly(False)
    
    #---------------------------------------------------------------------------
    
    def _setupProjectStatus(self):
        
        stdout, stderr = utils.runSubprocess('git status',
            cwd=os.path.dirname(
            os.path.dirname(self.parentApplication.installer.mainModulePath)))
                
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
        
        self.utrackedFilesListWidget.clear()
        
        for untrackedFile in untrackedFiles:
            self.utrackedFilesListWidget.addItem(
                bw.BaseListWidgetItem(self, untrackedFile))

    #--------------------------------------------------------------------------
    
    def setupContent(self):
        
        self.commitMessageTextEdit.clear()
        
        self._setupTagList()
        self._setupProjectStatus()
        
        self.hasFinished.emit()
        
    #---------------------------------------------------------------------------
    
#     def getCommitMessage(self):
#         
#         message = str(self.commitMessageTextEdit.toPlainText())
#         
#         if len(message) == 0:
#             raise RevisionException('Please add commit description.')
#         
#         return message
    
#     #---------------------------------------------------------------------------
#     
#     def getNewFilesToAdd(self):
#     
#         newFileList = list()
#         for i in range(self.utrackedFilesListWidget.count()):
#             item = self.utrackedFilesListWidget.item(i)
#             if item.checkState() == QtCore.Qt.Checked:
#                 newFileList.append(str(item.text()))
#         
#         return newFileList
    
    #---------------------------------------------------------------------------
    
#     def getTagName(self):
#         return str(self.tagCombobox.currentText())
            
#==============================================================================


