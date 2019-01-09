#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi

import dialogs

#=============================================================================

INSTALL_CONFIG_WIDGETS = dict()

#==============================================================================

class BaseListWidgetItem(QtGui.QListWidgetItem):
    
    def __init__(self, parentWidget, name):
        super(BaseListWidgetItem, self).__init__()
        
        self.parentWidget = parentWidget
        self.parentApplication = parentWidget.parentApplication
        self.name = name
        
        self.setFlags(self.flags()|QtCore.Qt.ItemIsTristate)
        self.setCheckState(QtCore.Qt.Unchecked)
        
        self.setText(self.name)
        
         
#===============================================================================
# 
# class CentralWidget(QtGui.QWidget):
#     
#     def __init__(self, mainWindow):
#         super(CentralWidget, self).__init__()
#         
#         self.mainWindow = mainWindow 
#         self.parentApplication = mainWindow.parentApplication
#         
#         self.execConfigWidgets = dict()
#         
#         self._setupWidgets()
#     
#     #--------------------------------------------------------------------------
# 
#     def _setupWidgets(self):
#                         
#         self.layout = QtGui.QVBoxLayout()
#         self.setLayout(self.layout)
#                 
#         # source project
#         groupSource = QtGui.QGroupBox('Source pyProject')
#         groupSource.setLayout(QtGui.QVBoxLayout())
#         self.layout.addWidget(groupSource)
#         
#         # install type
#         self.installTypeComboBox = QtGui.QComboBox()
#         
#         layout = QtGui.QHBoxLayout()
#         layout.addWidget(QtGui.QLabel('Install type'))
#         layout.addWidget(self.installTypeComboBox)
#         groupSource.layout().addLayout(layout)
#         
#         # source file 
#         self.sourcePyProjectLineEdit = QtGui.QLineEdit()
#         self.browseButton = QtGui.QPushButton('Browse')
#         
#         layout = QtGui.QHBoxLayout()
#         layout.addWidget(QtGui.QLabel('Source pyProject'))
#         layout.addWidget(self.sourcePyProjectLineEdit)
#         layout.addWidget(self.browseButton)
#         groupSource.layout().addLayout(layout)
#         
#         # documentation
#         groupDoc = QtGui.QGroupBox('Documentation')
#         groupDoc.setLayout(QtGui.QVBoxLayout())
#         self.layout.addWidget(groupDoc)
#         
#         layout = QtGui.QGridLayout()
#         groupDoc.layout().addLayout(layout)
#         
#         # documentation group
#         self.docuGroupCombobox = DocumentationGroupComboBox(self)
#          
#         layout.addWidget(QtGui.QLabel('Tool group'), 0, 0)
#         layout.addWidget(self.docuGroupCombobox, 0, 1)
#         
#         # documentation description
#         self.docuDescription = QtGui.QLineEdit()
#         
#         layout.addWidget(QtGui.QLabel('Tool description'), 1, 0)
#         layout.addWidget(self.docuDescription, 1, 1)
#         
#         # documentation string
#         self.documentationTextEdit = QtGui.QTextEdit()
#         self.documentationTextEdit.setReadOnly(True)
#         
#         font = QtGui.QFont()
#         font.setFamily("Courier New")
#         self.documentationTextEdit.setFont(font)
#         
#         groupDoc.layout().addWidget(self.documentationTextEdit)
#         
#         layout = QtGui.QHBoxLayout()
#         layout.addStretch()
#         
#         # enable editing
#         self.editDocStringButton = QtGui.QPushButton('Edit')
#                 
#         layout.addWidget(self.editDocStringButton)
#         
#         # default documentation string
#         self.dftDocStringButton = QtGui.QPushButton('Default doc')
#         self.dftDocStringButton.setEnabled(False)
#         
#         layout.addWidget(self.dftDocStringButton)
#         
#         # preview
#         self.previewButton = QtGui.QPushButton('Preview')
#                 
#         layout.addWidget(self.previewButton)
#         groupDoc.layout().addLayout(layout)
#         
#         # execution
#         groupExec = QtGui.QGroupBox('Execution settings')
#         groupExec.setLayout(QtGui.QVBoxLayout())
#         self.layout.addWidget(groupExec)
#         
#         self.executableStackedWidget = QtGui.QStackedWidget()
#         
#         groupExec.layout().addWidget(self.executableStackedWidget)
#         
#         
#         for execConfigWidget in INSTALL_CONFIG_WIDGETS.values():
#             currentWidget = execConfigWidget(self)
#             
#             self.executableStackedWidget.addWidget(currentWidget)
#             
#             # register added widget for easier switching
#             self.execConfigWidgets[
#                 currentWidget.NAME] = self.executableStackedWidget.indexOf(currentWidget)
#                 
#         # installation
#         groupInstall = QtGui.QGroupBox('Installation')
#         groupInstall.setLayout(QtGui.QVBoxLayout())
#         self.layout.addWidget(groupInstall)
#         
#         layout = QtGui.QGridLayout()
#         groupInstall.layout().addLayout(layout)
#                 
#         # revision
#         self.tagCombobox = ProjectTagComboBox(self)
#          
#         layout.addWidget(QtGui.QLabel('Select version'), 0, 0)
#         layout.addWidget(self.tagCombobox, 0, 1)
# 
# 
#         # buttons
#         frame = QtGui.QFrame()
#         frame.setFrameShape(QtGui.QFrame.HLine)
#         self.layout.addWidget(frame)
#         
#         self.buttonBox = QtGui.QDialogButtonBox()
#         self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
#         
#         self.installButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
#         self.closeButton = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
#         
#         self.layout.addWidget(self.buttonBox)
#         
#         # setup user info
#         userInfo = QtGui.QLabel('Current user: %s@%s' % (
#         self.parentApplication.userName, self.parentApplication.machine))
#         
#         self.buttonBox.layout().insertWidget(0, userInfo)
#     
#     #--------------------------------------------------------------------------
# 
#     def setDocuDescription(self, text):
#         
#         if len(text) > 0:
#             self.docuDescription.clear()
#             self.docuDescription.setText(text)
#         
#     #--------------------------------------------------------------------------
# 
#     def setDocString(self, text):
#         
#         if len(self.documentationTextEdit.toPlainText()) > 0:
#             answer = QtGui.QMessageBox.question(
#                 self.mainWindow, '%s' % self.parentApplication.APPLICATION_NAME,
#                 'Current documentation string will be deleted. Do you want to continue?',
#                 QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
#             if answer == QtGui.QMessageBox.No:
#                 return
#         
#         self.documentationTextEdit.clear()
#         self.documentationTextEdit.setText(text)
#     
#     #--------------------------------------------------------------------------
#     
#     def getDocString(self):
#         
#         return str(self.documentationTextEdit.toPlainText())
#     
#     #--------------------------------------------------------------------------
#     
#     def setExecSettingsFromMainModule(self, mainModule):
#         
#         for execConfigWidgetNo in self.execConfigWidgets.values():
#             
#             execConfigWidget = self.executableStackedWidget.widget(execConfigWidgetNo)
#             execConfigWidget.setExecSettingsFromMainModule(mainModule)
#     
#     #--------------------------------------------------------------------------
#     
#     def enableDocStringEditing(self):
#         
#         answer = QtGui.QMessageBox.question(
#             self.mainWindow, '%s' % self.parentApplication.APPLICATION_NAME,
#             'When you edit the documentation string you will have to create a new program version. \nDo you want to continue?',
#             QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
#         if answer == QtGui.QMessageBox.No:
#             return
#         
#         self.documentationTextEdit.setReadOnly(False)
#         self.dftDocStringButton.setEnabled(True)
            
#==============================================================================

class BaseExtendableComboBox(QtGui.QComboBox):
    
    NEW_ITEM_TEXT = '+ add a new item'
    NEW_ITEM_WINDOW_LABEL = 'New item'
    NEW_ITEM_DESCRIPTION = 'Select new item name'
    DFT_INDEX = -1
    
    itemAdded = QtCore.pyqtSignal(str)

    def __init__(self, mainWindow):
        super(BaseExtendableComboBox, self).__init__()
        
        self.mainWindow = mainWindow
        self.parentApplication = mainWindow.parentApplication

        self._setupItems()
        
        self.currentIndexChanged.connect(self._checkItem)

    #---------------------------------------------------------------------------
    
    def _setupItems(self):
        
        pass
      
    #--------------------------------------------------------------------------
    
    def _checkItem(self):
        
        if self.currentText() == self.NEW_ITEM_TEXT:
            self._createNewItem()
    
    #--------------------------------------------------------------------------
    
    def addNewItem(self, newGroupName):
        
        self.blockSignals(True)
        
        # group already present
        if self.findText(newGroupName) != -1:
            self.setCurrentIndex(self.findText(newGroupName))
        elif len(str(newGroupName).strip()) > 0:
            self.insertItem(0, newGroupName)
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(0)
#             raise PyProjectInstallerException('Invalid group name "%s"' % newGroupName)
        
        self.blockSignals(False)
        
        self.currentIndexChanged.emit(self.currentIndex())
    
    #--------------------------------------------------------------------------
    
    def _createNewItem(self):
        
        newGroupName, ok = QtGui.QInputDialog.getText(self.mainWindow,
            self.NEW_ITEM_WINDOW_LABEL, self.NEW_ITEM_DESCRIPTION)
            
        if not ok:
            self.setCurrentIndex(self.DFT_INDEX)
            return
        
        self.addNewItem(newGroupName)
        self.itemAdded.emit(newGroupName)
    
    #---------------------------------------------------------------------------
    
    def clear(self):
        
        super(BaseExtendableComboBox, self).clear()
        
        self.blockSignals(True)
        
        self.addItem(self.NEW_ITEM_TEXT)
        self.setCurrentIndex(self.DFT_INDEX)
        
        self.blockSignals(False)
        
        
#==============================================================================

class DocumentationGroupComboBox(BaseExtendableComboBox):
    
    DOCU_GROUPS_PATH = '/data/fem/+software/SKRIPTY/tools/python/tool_documentation/default/source'
    NEW_ITEM_TEXT = '+ add a new group'
    NEW_ITEM_WINDOW_LABEL = 'New tool group'
    NEW_ITEM_DESCRIPTION = 'Select new tool documentation group name'
    DFT_INDEX = 0
    
    #---------------------------------------------------------------------------
    
    def _setupItems(self):
        
        for item in os.listdir(self.DOCU_GROUPS_PATH):
            if os.path.isdir(os.path.join(self.DOCU_GROUPS_PATH, item)):
                self.addItem(item)
        
        self.addItem(self.NEW_ITEM_TEXT)
        
    
        
#==============================================================================

class ProjectTagComboBox(BaseExtendableComboBox):
    
    NEW_ITEM_TEXT = '+ new version'
    NEW_ITEM_WINDOW_LABEL = 'New version tag'
    NEW_ITEM_DESCRIPTION = 'Select new tool version tag (e.g. V.0.0.1).'

    #---------------------------------------------------------------------------
    
    def _setupItems(self):
                
        self.addItem(self.NEW_ITEM_TEXT)
        
        self.setCurrentIndex(-1)
    
    #---------------------------------------------------------------------------
    
    def setupTagList(self, tagList):
        
        self.clear()
        
        for tag in tagList:
            self.addNewItem(tag)
        
        
        
#             super(ProjectTagComboBox, self).addNewItem(tag)
    
    #---------------------------------------------------------------------------
    
#     def addNewItem(self, tagName):
#         
#         newRevisionDialog = dialogs.NewRevisionDialog(self.parentApplication, tagName)
#         result = newRevisionDialog.exec_()
#         
#         if result == QtGui.QDialog.Accepted:
#             super(ProjectTagComboBox, self).addNewItem(tagName)
#         else:
#             self.setCurrentIndex(-1)
#             
#             message = 'New revision not handled.'
#             QtGui.QMessageBox.critical(
#                 self.mainWindow, '%s' % self.parentApplication.APPLICATION_NAME,
#                 message)
            

#==============================================================================

class BaseItemParamSyncWidget(QtGui.QWidget):

    #---------------------------------------------------------------------------
    
    def _connectLineEditWidget(self, widget, paramName):
                
        widget.textChanged.connect(
            lambda: self.installationItem.setParamValue(
                paramName, str(widget.text())))
    
    #---------------------------------------------------------------------------
    
    def _connectTextEditWidget(self, widget, paramName):
                
        widget.textChanged.connect(
            lambda: self.installationItem.setParamValue(
                paramName, str(widget.toPlainText())))

    #---------------------------------------------------------------------------
    
    def _connectComboBoxWidget(self, widget, paramName):
                
        widget.currentIndexChanged.connect(
            lambda: self.installationItem.setParamValue(
                paramName, str(widget.currentText())))

    #---------------------------------------------------------------------------
    
    def _connectListWidget(self, widget, paramName):
        
        def getListWidgetItems():
            newList = list()
            for i in range(widget.count()):
                item = widget.item(i)
                if item.checkState() == QtCore.Qt.Checked:
                    newList.append(str(item.text()))
            
            return newList
    
        widget.itemClicked.connect(
            lambda: self.installationItem.setParamValue(
                paramName, getListWidgetItems()))
    
#==============================================================================

class BaseConfigExecutableWidget(BaseItemParamSyncWidget):
    
    container = INSTALL_CONFIG_WIDGETS
    NAME = ''

    def __init__(self, parentStack):
        super(BaseConfigExecutableWidget, self).__init__()
        
        self.parentStack = parentStack
        self.installer = self.parentStack.parentApplication.installer
        
        self.installationItem = bi.INSTALL_TYPES[self.NAME](self.installer)
        
        self._setupWidgets()
        self._setupConnections()
        
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        pass
    
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        pass
    
    #---------------------------------------------------------------------------
    
    def setExecSettingsFromMainModule(self):
                        
        self.setProjectName(self.installer.mainModuleItem.applicationName)
    
    #---------------------------------------------------------------------------
    
    def setProjectName(self, projectName):
        
        pass
    

    
    
#==============================================================================
@utils.registerClass
class ExecConfigExecutableWidget(BaseConfigExecutableWidget):
    
    NAME = bi.BaseInstallType.TYPE_EXECUTABLE
        
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QGridLayout())
                
        # executable
        self.executableLineEdit = QtGui.QLineEdit()
        
        self.layout().addWidget(QtGui.QLabel('Executable name'), 0, 0)
        self.layout().addWidget(self.executableLineEdit, 0, 1)
        
#         self.execFunctionNameComboBox = QtGui.QComboBox()
#         
#         self.layout().addWidget(QtGui.QLabel('Function name'), 1, 0)
#         self.layout().addWidget(self.execFunctionNameComboBox, 1, 1)
        
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self._connectLineEditWidget(self.executableLineEdit, 'executableName')
    
    #---------------------------------------------------------------------------
    
    def setProjectName(self, projectName):
                    
        self.executableLineEdit.clear()
        self.executableLineEdit.setText(projectName)
        
#==============================================================================
@utils.registerClass
class ExecConfigAnsaButtonWidget(BaseConfigExecutableWidget):
    
    NAME = bi.BaseInstallType.TYPE_ANSA_BUTTON

    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QGridLayout())
                
        self.buttonGroupLineEdit = QtGui.QLineEdit()
        
        self.layout().addWidget(QtGui.QLabel('Button group name'), 0, 0)
        self.layout().addWidget(self.buttonGroupLineEdit, 0, 1)
        
        self.buttonNameLineEdit = QtGui.QLineEdit()
        
        self.layout().addWidget(QtGui.QLabel('Button name'), 1, 0)
        self.layout().addWidget(self.buttonNameLineEdit, 1, 1)
        
        self.execFunctionNameComboBox = QtGui.QComboBox()
         
        self.layout().addWidget(QtGui.QLabel('Exec. function name'), 2, 0)
        self.layout().addWidget(self.execFunctionNameComboBox, 2, 1)

    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self._connectLineEditWidget(self.buttonGroupLineEdit, 'buttonGroupName')
        self._connectLineEditWidget(self.buttonNameLineEdit, 'buttonName')
        self._connectComboBoxWidget(self.execFunctionNameComboBox, 'execFunction')
          
    #---------------------------------------------------------------------------
    
    def setProjectName(self, projectName):
                    
        self.buttonNameLineEdit.clear()
        self.buttonNameLineEdit.setText(projectName)
        
        self.buttonGroupLineEdit.clear()
        
        # setup exec function combobox
        self.execFunctionNameComboBox.clear()
        
        # in case there is a decorator for ansa button present
        buttonExecFunctions = self.installer.mainModuleItem.getListOfAnsaButtonDecoratedFunctions()
        if len(buttonExecFunctions) > 0:
            for buttonExecFunction in buttonExecFunctions:
                for functionName, settings in buttonExecFunction.iteritems():
                    
                    self.buttonGroupLineEdit.setText(settings[0])
                    self.buttonNameLineEdit.setText(settings[1])
            
            self.buttonGroupLineEdit.setEnabled(False)
            self.buttonNameLineEdit.setEnabled(False)
            
            self.execFunctionNameComboBox.addItem(functionName)
            self.execFunctionNameComboBox.setEnabled(False)
            
            self.installationItem.decoratorPresent = True
        else:
            
            self.buttonGroupLineEdit.setEnabled(True)
            self.buttonNameLineEdit.setEnabled(True)
            self.execFunctionNameComboBox.setEnabled(True)
            
            listOfFuntions = self.installer.mainModuleItem.getListOfFunctions()
            for functionName in listOfFuntions.keys():
                self.execFunctionNameComboBox.addItem(functionName)
            
            self.installationItem.decoratorPresent = False
     
        
#==============================================================================
@utils.registerClass
class ExecConfigMetaWidget(BaseConfigExecutableWidget):
    
    NAME = bi.BaseInstallType.TYPE_META

    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QGridLayout())
                
        # executable
        self.toolbarNameLineEdit = QtGui.QLineEdit()
        
        self.layout().addWidget(QtGui.QLabel('Toolbar name'), 0, 0)
        self.layout().addWidget(self.toolbarNameLineEdit, 0, 1)

        self.buttonNameLineEdit = QtGui.QLineEdit()
        
        self.layout().addWidget(QtGui.QLabel('Button name'), 1, 0)
        self.layout().addWidget(self.buttonNameLineEdit, 1, 1)

    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self._connectLineEditWidget(self.toolbarNameLineEdit, 'toolbarName')
        self._connectLineEditWidget(self.buttonNameLineEdit, 'buttonName')
        
    #---------------------------------------------------------------------------
    
    def setProjectName(self, projectName):
                    
        self.buttonNameLineEdit.clear()
        self.buttonNameLineEdit.setText(projectName)
        
#==============================================================================
