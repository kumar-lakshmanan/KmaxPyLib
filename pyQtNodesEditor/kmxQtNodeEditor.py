'''
Created on Oct 2, 2017

@author: npn
'''

from PyQt5.QtCore import (QEvent,QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, QObject,QSizeF, QRectF, QPointF,)
from PyQt5.QtWidgets import (QGraphicsView,QGraphicsScene,QGraphicsPathItem,QGraphicsTextItem, QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QSizePolicy, QGraphicsSceneMouseEvent, QGraphicsItem)
from PyQt5.QtGui import (QPainter,QBrush,QFontMetrics,QPainterPath, QIcon, QKeySequence, QFont, QColor,QPen)
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython, QsciAPIs)
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets

from pyQtNodesEditor import nodeEditor as ne

import kmxTools
import sys
sys.excepthook = kmxTools.errorHandler

class KMXFlowConnection():
    
    def __init__(self, srcBlock, dstBlock, srcPort, dstPort, neConn):
        self.srcBlock = srcBlock
        self.dstBlock = dstBlock
        self.srcPort = srcPort
        self.dstPort = dstPort
        self.neConn = neConn

    def connectionDetail(self):
        src = self.srcBlock._fcBlock.name
        dst = self.dstBlock._fcBlock.name
        srcP = self.srcPort.portName()
        dstP = self.dstPort.portName()
        print('{0}.{1} --> {2}.{3}'.format(src,srcP,dst,dstP))

class KMXFlowBlock(object):
    
    def __init__(self, name, type='', inputs=['inp1','inp2'], outputs=['out']):
        self.name = name
        self.type = type
        self.inputs = inputs
        self.outputs = outputs 
        self.chart = None
        self.blockParent = None
        self.scene = None
        self.neBlock = None             
        self.connectionInput = {}
        self.connectionOutput = {}
        
    def _addToScene(self, chart, scene, blockParent=None):
        self.chart = chart
        self.blockParent = blockParent
        self.scene = scene
        self.neBlock = ne.QNEBlock(blockParent)
        self.scene.addItem(self.neBlock)
        
        #BlockName
        self.neBlock.addPort(self.name, 0, ne.QNEPort.NamePort, self)
        
        #BlockType
        self.neBlock.addPort(self.type, 0, ne.QNEPort.TypePort, self)
        
        #Block Inputs
        if(len(self.inputs) == len(set(self.inputs))): 
            for eachInput in self.inputs:
                self.neBlock.addInputPort(eachInput);
        else:
            print('Duplicate input found, Unable to add to block. ' + str(self.inputs))

        #Block Outputs
        if(len(self.outputs) == len(set(self.outputs))):
            for eachOutput in self.outputs:
                self.neBlock.addOutputPort(eachOutput);
        else:
            print('Duplicate output found, Unable to add to block. ' + str(self.outputs))

    def addInput(self, inputName):
        if(not inputName in self.inputs):
            self.inputs.append(inputName)
            if(self.neBlock):
                self.neBlock.addInputPort(inputName);   
        else:
            print('{0} already available in input list: {1}, cannot add to {2} block.'.format(inputName, str(self.inputs), self.name))

    def addOutput(self, outputName):
        if(not outputName in self.outputs):
            self.outputs.append(outputName)
            if(self.neBlock):
                self.neBlock.addOutputPort(outputName);        
        else:
            print('{0} already available in output list: {1}, cannot add to {2} block.'.format(outputName, str(self.outputs), self.name))

class KMXFlowChart(QGraphicsView):
    '''
    classdocs
    '''

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(KMXFlowChart, self).__init__(parent)
        self.parent = parent
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.core = ne.QNodesEditor(self)
        self.core.install(self.scene)
        
        self.blocks = []
        self.connections = []
        
        self.core.sigBlockConnected.connect(self._guiBlockConnects)
        self.core.sigBlockDisconnected.connect(self._guiBlockDisconnects)
        self.core.sigContextAct.connect(self.doAct)
        
    def addBlock(self, block):
        if(block and type(block)==type(KMXFlowBlock(None))):
            print('Adding new block..' + str(block.name))
            block._addToScene(self, self.scene, None)
            self.blocks.append(block)
        
    def removeBlock(self, block):
        #Remove Connections
        for eachConn in self.connections:
            if eachConn.srcBlock == block.neBlock or eachConn.dstBlock == block.neBlock:
                self.connections.remove(eachConn)
                 
        self.blocks.remove(block)
        block.neBlock.delete()
                   
    def disconnectBlocks(self, srcBlock, outputNode, dstBlock, inputNode):
        conn = self._findConn(srcBlock, outputNode, dstBlock, inputNode)
        if(conn and type(conn)==type(KMXFlowConnection(None,None,None,None))):
            self._guiBlockDisconnects(conn.neConn)
            conn.neConn.delete()
        else:
            print('Invalid connection')
                                        
    def connectBlocks(self, srcBlock, outputNode, dstBlock, inputNode):
        #Verification
        src = self._getPort(srcBlock.neBlock, outputNode)
        dst = self._getPort(dstBlock.neBlock, inputNode)
        
        if src.block() != dst.block() and  src.isOutput() != dst.isOutput() and not src.isConnected(dst):
            conn = ne.QNEConnection(None)
            self.scene.addItem(conn)
            conn.setPort1(src)
            conn.setPos1(src.scenePos())
            conn.setPort2(dst)
            conn.setPos2(dst.scenePos())  
            conn.updatePath()     
            self._guiBlockConnects(conn) 
        else:
            print('Invalid connection or connection already exist')
        
    def _getPort(self, neBlock, searchPortName):
        for eachPort in neBlock.ports():
            if searchPortName == eachPort.portName():
                return eachPort
        
    def _findConn(self, srcBlock, outputNode, dstBlock, inputNode):
        for eachConn in self.connections:
            if (eachConn.srcBlock == srcBlock.neBlock and
                eachConn.srcPort.portName() == outputNode and
                eachConn.dstBlock == dstBlock.neBlock and 
                eachConn.dstPort.portName() == inputNode):
                return eachConn
            
    def doAct(self):
        print('Act')
        print(self.connections)
        print(self.blocks)
    
    def _guiBlockConnects(self, parent):
        srcBlock = parent.m_port1.block() 
        dstBlock = parent.m_port2.block() 
        srcPort = parent.m_port1 
        dstPort = parent.m_port2

        conn = KMXFlowConnection(srcBlock, dstBlock, srcPort, dstPort, parent)
        parent._fcConnection = conn
        self.connections.append(conn)
        conn.connectionDetail()

    def _guiBlockDisconnects(self,parent):
        conn = parent._fcConnection
        self.connections.remove(conn)
        conn.connectionDetail()

                
        
class MyEditor(QMainWindow):        
    def __init__(self, parent):
        super(MyEditor, self).__init__(parent)
        self.setWindowTitle("Node Editor")

        self.fc = KMXFlowChart(self)     
           
        self.setCentralWidget(self.fc)
        
        addition = KMXFlowBlock('Add','Addr',['inp1','inp3'],['out'])
        subtraction = KMXFlowBlock('Sub','',['inp1','inp2'],['out'])
        mul = KMXFlowBlock('mul','',['inp1','inp2'],['out'])
       
        self.fc.addBlock(addition)
        self.fc.addBlock(subtraction)
        self.fc.addBlock(mul)

        addition.neBlock.setPos(0,150)
        subtraction.neBlock.setPos(150,150)        
        mul.neBlock.setPos(75,75)
        
        print(addition)
        print(subtraction)
        self.fc.connectBlocks(addition,'out',subtraction,'inp2')
        
        #self.fc.connectBlocks(addition,'out',subtraction,'out')
        #self.fc.connectBlocks(addition,'out',addition,'inp1')
        #self.fc.connectBlocks(addition,'out',subtraction,'inp1')
        #self.fc.connectBlocks(mul,'out',subtraction,'inp1')
        self.fc.disconnectBlocks(addition,'out',subtraction,'inp3')
        
        self.fc.removeBlock(subtraction)
        
       
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = MyEditor(None)
    widget.show()
    sys.exit(app.exec_())        