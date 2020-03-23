#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

from functools import partial
import numpy as np

from PyQt4 import QtCore
from PyQt4 import QtGui

from domain import utils
# from domain import base_items as bi


#=============================================================================

class BaseTreeItem(QtGui.QStandardItem):
    
    ICON_PATH = ''
    
    def __init__(self, dataItem):
        
        self.dataItem = dataItem
        
        super(BaseTreeItem, self).__init__(self.dataItem.NAME)
        
        self.setIcon(QtGui.QIcon(self.ICON_PATH))
        self.setToolTip(self.dataItem.NAME)
        self.setEditable(False)
    
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentView):
        
        menu = QtGui.QMenu()
        collapseAction = menu.addAction("Collapse children")
        collapseAction.triggered.connect(lambda: self._collapseChildren(parentView))
        
        menu.exec_(QtGui.QCursor.pos())
    
    #------------------------------------------------------------------------------ 
    
    def _collapseChildren(self, parentView):
            
        for row in range(self.rowCount()):
            child = self.child(row)
            parentView.collapse(child.index())



#=============================================================================

class ToolTreeItem(QtGui.QStandardItem):
    
    DFT_COLOUR = QtGui.QBrush(QtCore.Qt.black)
    COLOUR_AVAILABLE_LOCALY = QtGui.QBrush(QtCore.Qt.gray)
    COLUMN_LABELS = ['Tool name', 'version', 'description']
    
    def __init__(self, parentGroupTreeItem, dataItem):
        
        self.dataItem = dataItem
        self.parentGroupTreeItem = parentGroupTreeItem
        
        super(ToolTreeItem, self).__init__(self.dataItem.name)
        
#         self.setIcon(QtGui.QIcon(self.ICON_PATH))
        self.setEditable(False)
        self.setData(self.dataItem, QtCore.Qt.UserRole)
                
        versionItem = QtGui.QStandardItem(self.dataItem.version())
        descriptionItem = QtGui.QStandardItem(self.dataItem.getOneLineDescription())
        versionItem.setEditable(False)
        descriptionItem.setEditable(False)
        
        if self.dataItem.isLocal():
            self.setEnabled(False)
            versionItem.setEnabled(False)
            descriptionItem.setEnabled(False)
            
#             self.setForeground(self.COLOUR_AVAILABLE_LOCALY)
#             versionItem.setForeground(self.COLOUR_AVAILABLE_LOCALY)
#             descriptionItem.setForeground(self.COLOUR_AVAILABLE_LOCALY)
            
            self.setToolTip('Available locally')
            versionItem.setToolTip('Available locally')
            descriptionItem.setToolTip('Available locally')
        else:
            self.setToolTip('Available in master repository')
            versionItem.setToolTip('Available in master repository')
            descriptionItem.setToolTip('Available in master repository')
        
        self.parentGroupTreeItem.appendRow([self, versionItem, descriptionItem])
            
    #------------------------------------------------------------------------------ 
    
    def setColour(self, rgb):
        
        self.setForeground(QtGui.QBrush(QtGui.QColor.fromRgbF(*rgb)))
    
    #------------------------------------------------------------------------------ 
    
    def setDftColour(self):
        
        self.setForeground(self.DFT_COLOUR)
        
    #------------------------------------------------------------------------------ 
    

#=================================================================================

class BaseTreeModel(QtGui.QStandardItemModel):
    
    def __init__(self, toolGroups):
        
        super(BaseTreeModel, self).__init__()
        
        self.toolGroups = toolGroups
        
        self.headerLabels = ToolTreeItem.COLUMN_LABELS
        self.setHorizontalHeaderLabels(self.headerLabels)
        
        self._setupContent()
        
    #------------------------------------------------------------------------------ 
    
    def _setupContent(self):
        
        for groupName in sorted(self.toolGroups.keys()):            
            
            groupItem = QtGui.QStandardItem(groupName)
            groupItem.setEditable(False)
            
            self.appendRow(groupItem)

            tools = self.toolGroups[groupName]
            for tool in tools:
                toolTreeItem = ToolTreeItem(groupItem, tool)
                
#                 print(tool.isLocal(), tool.name, tool.version(), )

#=================================================================================
    





















