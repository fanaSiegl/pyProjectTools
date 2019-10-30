#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi

from presentation import dialogs

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
            self.NEW_ITEM_WINDOW_LABEL, self.NEW_ITEM_DESCRIPTION,
            text=self._getDefaultNewItemText())
            
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
    
    #---------------------------------------------------------------------------
    
    def _getDefaultNewItemText(self):
        
        return ''    
        
#==============================================================================

class DocumentationGroupComboBox(BaseExtendableComboBox):
    
    DOCU_GROUPS_PATH = utils.getInstallTypePaths()[
        'INSTALLATION_PATHS_BASE']['DOCUMENTATON_PATH']
    NEW_ITEM_TEXT = '+ add a new group'
    NEW_ITEM_WINDOW_LABEL = 'New tool group'
    NEW_ITEM_DESCRIPTION = 'Select new tool documentation group name'
    DFT_INDEX = 0
    
    #---------------------------------------------------------------------------
    
    def _setupItems(self):
        
        toolGroups = set()
        
        sourcePath = os.path.join(self.DOCU_GROUPS_PATH, 'res', 'source')
        if os.path.exists(sourcePath):
            for location in os.listdir(sourcePath):
                if os.path.isdir(os.path.join(sourcePath, location)):
                
                    for item in os.listdir(os.path.join(sourcePath, location)):
                        if os.path.isdir(os.path.join(sourcePath, location, item)):
                            toolGroups.add(item)
            
            for toolGroup in toolGroups:
                self.addItem(toolGroup)
        
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
        
    #---------------------------------------------------------------------------
    
    def _getDefaultNewItemText(self):
        
        versions = list()
        for itemIndex in range(self.count()):
            itemText = self.itemText(itemIndex)
            if itemText.startswith('V'):
                versions.append(itemText)
        
        if len(versions) == 0:
            return 'V.0.0.1'
            
        try:
            lastVersion = sorted(versions)[-1]
            parts = lastVersion.split('.')
            parts[-1] = str(int(parts[-1]) + 1) 
            nextVersion = '.'.join(parts) 
        except:
            nextVersion = ''
        
        return nextVersion
        
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

class CodeTypeComboBox(BaseExtendableComboBox):
    
    NEW_ITEM_TEXT = '+ new language'
    NEW_ITEM_WINDOW_LABEL = 'New language'
    NEW_ITEM_DESCRIPTION = 'Select new programming language group.'
    
    DFT_LANGUAGE = 'python'    
    TOOL_ROOT = utils.getInstallTypePaths()['INSTALLATION_PATHS_TYPE_EXECUTABLE']['PRODUCTIVE_VERSION_HOME']
    IGNORE_ROOT_DIRS = ['bin', 'repos']

    #---------------------------------------------------------------------------
    
    def _setupItems(self):
                
        for language in self._getListOfAvailableLanguages():
            self.addItem(language)
        
        self.DFT_INDEX = self.findText(self.DFT_LANGUAGE)
        
        self.addItem(self.NEW_ITEM_TEXT)
                
        self.setCurrentIndex(self.DFT_INDEX)
    
    #---------------------------------------------------------------------------
    
    def _getListOfAvailableLanguages(self):
        
        languages = list()
        
        for itemName in os.listdir(self.TOOL_ROOT):
            if (os.path.isdir(os.path.join(self.TOOL_ROOT, itemName)) and  
                itemName not in self.IGNORE_ROOT_DIRS):
                
                languages.append(itemName)
        return languages 
    
            
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
        
        self.codeLanguageComboBox = CodeTypeComboBox(
            self.parentStack.mainWindow)
         
        self.layout().addWidget(QtGui.QLabel('Programming language'), 1, 0)
        self.layout().addWidget(self.codeLanguageComboBox, 1, 1)
        
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self._connectLineEditWidget(self.executableLineEdit, 'executableName')
        self._connectComboBoxWidget(self.codeLanguageComboBox, 'codeLanguage')
    
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
                
        self.buttonGroupLineEdit.clear()
        
        # setup exec function combobox
        self.execFunctionNameComboBox.clear()
        
        # in case there is a decorator for ansa button present
        buttonExecFunctions = self.installer.mainModuleItem.getListOfAnsaButtonDecoratedFunctions()
        if len(buttonExecFunctions) > 0:
            for buttonExecFunction in buttonExecFunctions:
                for functionName, settings in buttonExecFunction.items():
                    
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
        
        # fill in button name 
        if len(projectName) > 0: 
            self.buttonNameLineEdit.clear()
            self.buttonNameLineEdit.setText(projectName)

#==============================================================================
@utils.registerClass
class ExecConfigAnsaCheckWidget(BaseConfigExecutableWidget):
    
    NAME = bi.BaseInstallType.TYPE_ANSA_CHECK
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
                
        self.buttonGroupLineEdit = QtGui.QLineEdit()
        
        installDescription = '''To add a new check after installation you have to
search for it in the ANSA Checks Manager and add it to the template.
Mind that only checks compatible with the current active DECK are listed.'''
        
        self.layout().addWidget(QtGui.QLabel(installDescription))

    #---------------------------------------------------------------------------
    
    def setExecSettingsFromMainModule(self):
        pass                
#         print(self.installer.mainModuleItem.applicationName)
        
        
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
