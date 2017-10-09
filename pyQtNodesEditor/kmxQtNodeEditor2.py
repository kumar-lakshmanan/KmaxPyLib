'''
Created on Oct 2, 2017

@author: npn
'''

from PyQt5.QtCore import (QEvent,QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, QObject,QSizeF, QRectF, QPointF,)
from PyQt5.QtWidgets import (QGraphicsView,QGraphicsScene,QGraphicsPathItem,QGraphicsTextItem, QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QSizePolicy, QGraphicsSceneMouseEvent, QGraphicsItem)
from PyQt5.QtGui import (QPainter,QBrush,QFontMetrics,QPainterPath, QIcon, QKeySequence, QFont, QColor,QPen)
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython, QsciAPIs)
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets

from pyQNodesEditor import nodeEditor as ne

class KMXFlowBlock(ne.QNEBlock):
    
    def __init__(self, chart, name='default', type='', parent=None):
        self.fcBlockName = name
        self.fcBlockType = type
        self.fcBlockParent = parent
        self.fcBlockChart = chart
        self.fcBlockScene = chart.scene
        self.fcBlockInputs=[]
        self.fcBlockOutputs=[]        
        ne.QNEBlock.__init__(self,self.fcBlockParent)
        self.fcBlockScene.addItem(self)
        self.fcBlockChart.kmxBlocks.append(self)
        if(self.fcBlockName): self.setBlockName(name)
        if(self.fcBlockType): self.setBlockType(type)
    
    def _blockRemoved(self):
        self.fcBlockChart.kmxBlocks.remove(self)
         
    def setBlockName(self, name):
        self.fcBlockName = name
        self.addPort(self.fcBlockName, 0, ne.QNEPort.NamePort, self)

    def setBlockType(self, type):
        self.fcBlockType = type
        self.addPort(self.fcBlockType, 0, ne.QNEPort.TypePort, self)
                        
    def addBlockInput(self,inputName):
        self.fcBlockInputs.append(inputName)
        self.addInputPort(inputName);

    def addBlockOutput(self,outputName):
        self.fcBlockOutputs.append(outputName)
        self.addOutputPort(outputName);        

class KMXFlowConnection():
    
    def __init__(self, srcBlock, dstBlock, srcPort, dstPort):
        self.srcBlock = srcBlock
        self.dstBlock = dstBlock
        self.srcPort = srcPort
        self.dstPort = dstPort

    def connectionDetail(self):
        src = self.srcBlock.fcBlock().fcBlockName
        dst = self.dstBlock.fcBlock().fcBlockName
        srcP = self.srcPort.portName()
        dstP = self.dstPort.portName()
        print('{0}.{1} --> {2}.{3}'.format(src,srcP,dst,dstP))

class KMXFlowChart(QGraphicsView):
    '''
    classdocs
    '''

    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(KMXFlowChart, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.core = ne.QNodesEditor(self)
        self.core.install(self.scene)
        
        self.kmxBlocks = []
        self.kmxBlockConnections = []
        
        self.core.sigBlockConnected.connect(self.blockConnects)
        self.core.sigBlockDisconnected.connect(self.blockDisconnects)
        self.core.sigContextAct.connect(self.doAct)
    
    def doAct(self):
        print(self.kmxBlockConnections)
        print(self.kmxBlocks)
    
    def blockConnects(self,parent):
        srcBlock = parent.m_port1.block() 
        dstBlock = parent.m_port2.block() 
        srcPort = parent.m_port1 
        dstPort = parent.m_port2
        kmxConn = KMXFlowConnection(srcBlock, dstBlock, srcPort, dstPort)
        parent.kmxBlockConnection = kmxConn
        self.kmxBlockConnections.append(kmxConn)
        kmxConn.connectionDetail()

    def blockDisconnects(self,parent):
        kmxConn = parent.kmxBlockConnection
        kmxConn.connectionDetail()
        self.kmxBlockConnections.remove(kmxConn)
                
        
class MyEditor(QMainWindow):        
    def __init__(self, parent):
        super(MyEditor, self).__init__(parent)
        self.setWindowTitle("Node Editor")

        self.fc = KMXFlowChart(self)        
        self.setCentralWidget(self.fc)
        
        add = KMXFlowBlock(self.fc,'Add','Addr')
        add.addBlockInput('inp1')
        add.addBlockInput('inp2')
        add.addBlockOutput('out')
        
        sub = KMXFlowBlock(self.fc,'Sub')
        sub.addBlockInput('inp1')
        sub.addBlockInput('inp2')
        sub.addBlockOutput('out')
        
        sub.setPos(150,150)
        
        print(self.fc.kmxBlocks)
        print(self.fc.kmxBlockConnections)
        
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = MyEditor(None)
    widget.show()
    sys.exit(app.exec_())        