'''
Created on Oct 24, 2015

@author: MUKUND
'''
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, )
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QDockWidget)
from PyQt5.QtGui import (QIcon, QKeySequence, QFont, QColor)
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython)
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets
from PyQt5.uic import loadUi
import os
import sys

import kmxQtMenuBuilder
import kmxQtCommonTools

class Tray(object):
    '''
    classdocs
    '''
    def __init__(self, parentWidget, trayClickFn=None, trayItemClickFn=None, trayIcon=None):
        '''
        Constructor
        '''
        self.parent = parentWidget
        self.trayClickFn = trayClickFn
        self.trayItemClickFn = trayItemClickFn
        self.trayIcon = trayIcon
        
        self.kmxMenuBuilder = kmxQtMenuBuilder.MenuBuilder()
        self.kmxQtTools = kmxQtCommonTools.CommonTools(None)
                
    def setupTray(self):
        self.tray = self.trayAgentReady(self.trayIcon)
        self.trayMenu = self.kmxMenuBuilder.createMenu(None, 'TrayMenu')
        self.tray.setContextMenu(self.trayMenu)

    def trayItemClicked(self, *arg):
        caller = self.parent.sender()        
        itm = caller.text()
        
        if(self.trayItemClickFn):
            self.trayItemClickFn(itm)
        
    def trayAgentReady(self, icon='roadworks.png'):    
        self.tray = QtWidgets.QSystemTrayIcon(self.kmxQtTools.getIcon(icon), self.parent)
        self.tray.activated.connect(self.trayClicked)        
        self.tray.show()
        return self.tray
    
    def trayClicked(self, click):   
        if(self.trayClickFn):
            self.trayClickFn(click)
               
    def trayMessage(self, messagetitle, message):
        self.tray.showMessage(messagetitle,message)
    
    def trayKiller(self):
        self.tray.hide()
        del(self.tray)                    

    def trayMenuUpdate(self, itemName, fnToCall=None):
        if fnToCall:
            return self.kmxMenuBuilder.updateMenu(self.parent, self.trayMenu, itemName, fnToCall)
        else:
            return self.kmxMenuBuilder.updateMenu(self.parent, self.trayMenu, itemName, self.trayItemClicked)