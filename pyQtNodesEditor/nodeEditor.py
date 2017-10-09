# Copyright (c) 2014, ALDO HOEBEN
# Copyright (c) 2012, STANISLAW ADASZEWSKI
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of STANISLAW ADASZEWSKI nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL STANISLAW ADASZEWSKI BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from PyQt5.QtCore import (pyqtSignal, QEvent,QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, QObject,QSizeF, QRectF, QPointF,)
from PyQt5.QtWidgets import (QGraphicsPathItem,QGraphicsTextItem, QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QSizePolicy, QGraphicsSceneMouseEvent, QGraphicsItem)
from PyQt5.QtGui import (QBrush,QFontMetrics,QPainterPath, QIcon, QKeySequence, QFont, QColor,QPen)
from PyQt5.Qsci import (QsciScintilla, QsciLexerPython, QsciAPIs)
from PyQt5 import QtCore, QtGui, Qsci, QtWidgets

class QNEBlock(QGraphicsPathItem):
    (Type) = (QGraphicsItem.UserType +3)

    def __init__(self, parent):
        super(QNEBlock, self).__init__(parent)

        path = QPainterPath()
        path.addRoundedRect(-50, -15, 100, 30, 5, 5);
        self.setPath(path)
        self.setPen(QPen(Qt.darkGreen))
        self.setBrush(Qt.green)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.horzMargin = 20
        self.vertMargin = 5
        self.width = self.horzMargin
        self.height = self.vertMargin
        self._fcBlock = None


    def __del__(self):
        #print("Del QNEBlock")
        pass


    def delete(self):
        for port in self.ports():
            for connection in port.connections():
                connection.delete()
            port.delete()
        self.scene().removeItem(self)


    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setPen(QPen(Qt.darkYellow))
            painter.setBrush(Qt.yellow)
        else:
            painter.setPen(QPen(Qt.darkGreen))
            painter.setBrush(Qt.green)

        painter.drawPath(self.path())


    def addPort(self, name, isOutput = False, flags = 0, ptr = None):
        port = QNEPort(self)
        port.setName(name)
        port.setIsOutput(isOutput)
        port.setNEBlock(self)
        port.setPortFlags(flags)
        
        if(flags == 1):
            self._fcBlock = ptr

        port.setPtr(ptr)
            
        fontmetrics = QFontMetrics(self.scene().font());
        width = fontmetrics.width(name)
        height = fontmetrics.height()
        if width > self.width - self.horzMargin:
            self.width = width + self.horzMargin
        self.height += height

        path = QPainterPath()
        path.addRoundedRect(-self.width/2, -self.height/2, self.width, self.height, 5, 5)
        self.setPath(path)

        y = -self.height / 2 + self.vertMargin + port.radius()
        for port_ in self.childItems():
            if port_.type() != QNEPort.Type:
                continue

            if port_.isOutput():
                port_.setPos(self.width/2 + port.radius(), y)
            else:
                port_.setPos(-self.width/2 - port.radius(), y)
            y += height;

        return port


    def addInputPort(self, name):
        self.addPort(name, False)


    def addOutputPort(self, name):
        self.addPort(name, True)


    def addInputPorts(self, names):
        for name in names:
            self.addInputPort(name)


    def addOutputPorts(self, names):
        for name in names:
            self.addOutputPort(name)


    def clone(self):
        block = QNEBlock(None)
        self.scene().addItem(block)

        for port_ in self.childItems():
            block.addPort(port_.portName(), port_.isOutput(), port_.portFlags(), port_.ptr())

        return block

    def ports(self):
        result = []
        for port_ in self.childItems():
            if port_.type() == QNEPort.Type:
                result.append(port_)

        return result

    def type(self):
        return self.Type

class QNEPort(QGraphicsPathItem):
    (NamePort, TypePort) = (1, 2)
    (Type) = (QGraphicsItem.UserType +1)

    def __init__(self, parent):
        super(QNEPort, self).__init__(parent)

        self.label = QGraphicsTextItem(self)
        self.radius_ = 4
        self.margin = 3

        path = QPainterPath()
        path.addEllipse(-self.radius_, -self.radius_, 2*self.radius_, 2*self.radius_);
        self.setPath(path)

        self.setPen(QPen(Qt.darkRed))
        self.setBrush(Qt.red)

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

        self.m_portFlags = 0
        self.isOutput_ = False

        self.m_block = None
        self.m_connections = []


    def __del__(self):
        #print("Del QNEPort %s" % self.name)
        pass


    def delete(self):
        for connection in self.m_connections:
            connection.delete()
        self.scene().removeItem(self)
        self.m_block = None
        self.m_connections = []


    def setName(self, name):
        self.name = name
        self.label.setPlainText(name)


    def setIsOutput(self, isOutput):
        self.isOutput_ = isOutput

        if self.isOutput_:
            self.label.setPos(-self.radius_ - self.margin - self.label.boundingRect().width(),
                -self.label.boundingRect().height()/2);
        else:
            self.label.setPos(self.radius_ + self.margin,
                -self.label.boundingRect().height()/2);



    def setNEBlock(self, block):
        self.m_block = block


    def setPortFlags(self, flags):
        self.m_portFlags = flags

        if self.m_portFlags & self.TypePort:
            font = self.scene().font()
            font.setItalic(True)
            self.label.setFont(font)
            self.setPath(QPainterPath())
        elif self.m_portFlags & self.NamePort:
            font = self.scene().font()
            font.setBold(True)
            self.label.setFont(font)
            self.setPath(QPainterPath())


    def setPtr(self, ptr):
        self.m_ptr = ptr


    def type(self):
        return self.Type


    def radius(self):
        return self.radius_


    def portName(self):
        return self.name


    def isOutput(self):
        return self.isOutput_


    def block(self):
        return self.m_block


    def portFlags(self):
        return self.m_portFlags


    def ptr(self):
        return self.m_ptr;


    def addConnection(self, connection):
        self.m_connections.append(connection)


    def removeConnection(self, connection):
        try:
            self.m_connections.remove(connection)
        except: pass


    def connections(self):
        return self.m_connections


    def isConnected(self, other):
        for connection in self.m_connections:
            if connection.port1() == other or connection.port2() == other:
                return True

        return False


    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for connection in self.m_connections:
                connection.updatePosFromPorts()
                connection.updatePath()

        return value

class QNEConnection(QGraphicsPathItem):
    (Type) = (QGraphicsItem.UserType +2)

    def __init__(self, parent):
        super(QNEConnection, self).__init__(parent)

        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QBrush(Qt.NoBrush))
        self.setZValue(-1)

        self.m_port1 = None
        self.m_port2 = None

        self.pos1 = QPointF()
        self.pos2 = QPointF()
        
        self._fcConnection = None


    def __del__(self):
        #print("Del QNEConnection")
        pass


    def delete(self):
        if self.m_port1:
            self.m_port1.removeConnection(self)
        if self.m_port2:
            self.m_port2.removeConnection(self)
        self.m_port1 = None
        self.m_port2 = None
        self.scene().removeItem(self)


    def setPos1(self, pos):
        self.pos1 = pos


    def setPos2(self, pos):
        self.pos2 = pos


    def setPort1(self, port):
        self.m_port1 = port
        self.m_port1.addConnection(self)


    def setPort2(self, port):
        self.m_port2 = port
        self.m_port2.addConnection(self)


    def updatePosFromPorts(self):
        self.pos1 = self.m_port1.scenePos()
        self.pos2 = self.m_port2.scenePos()


    def updatePath(self):
        path = QPainterPath()
        path.moveTo(self.pos1)

        dx = self.pos2.x() - self.pos1.x()
        dy = self.pos2.y() - self.pos1.y()

        ctr1 = QPointF(self.pos1.x() + dx * 0.25, self.pos1.y() + dy * 0.1)
        ctr2 = QPointF(self.pos1.x() + dx * 0.75, self.pos1.y() + dy * 0.9)

        path.cubicTo(ctr1, ctr2, self.pos2)
        self.setPath(path)


    def type(self):
        return self.Type


    def port1(self):
        return self.m_port1


    def port2(self):
        return self.m_port2

class QNodesEditor(QObject):

    sigBlockConnected = pyqtSignal(object)  # self, term
    sigBlockDisconnected = pyqtSignal(object)  # self, term
    sigContextAct = pyqtSignal()  # self, term
    
    def __init__(self, parent):
        super(QNodesEditor, self).__init__(parent)

        self.connection = None


    def install(self, scene):
        self.scene = scene
        self.scene.installEventFilter(self)


    def itemAt(self, position):
        items = self.scene.items(QRectF( position - QPointF(1,1) , QSizeF(3,3) ))

        for item in items:
            if item.type() > QGraphicsItem.UserType:
                return item

        return None;


    def eventFilter(self, object, event):
        if event.type() == QEvent.GraphicsSceneMousePress:

            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item and item.type() == QNEPort.Type:
                    self.connection = QNEConnection(None)
                    self.scene.addItem(self.connection)

                    self.connection.setPort1(item)
                    self.connection.setPos1(item.scenePos())
                    self.connection.setPos2(event.scenePos())
                    self.connection.updatePath()
                    
                    return True

            elif event.button() == Qt.RightButton:
                item = self.itemAt(event.scenePos())

                if item and (item.type() == QNEConnection.Type or item.type() == QNEBlock.Type):
                    if item.type() == QNEConnection.Type:
                        self.sigBlockDisconnected.emit(item)
                        item.delete()
                    elif item.type() == QNEBlock.Type:
                        item.delete()

                    return True
                else:
                    self.sigContextAct.emit()


        elif event.type() == QEvent.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.setPos2(event.scenePos())
                self.connection.updatePath()                
                return True

                
        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            
                
            if self.connection and event.button() == Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item and item.type() == QNEPort.Type:
                    port1 = self.connection.port1()
                    port2 = item

                    if port1.block() != port2.block() and port1.isOutput() != port2.isOutput() and not port1.isConnected(port2):

                        self.connection.setPos2(port2.scenePos())
                        self.connection.setPort2(port2)
                        self.connection.updatePath()
                        self.sigBlockConnected.emit(self.connection)
                        self.connection = None                        
                        return True
                    
                self.sigBlockConnected.emit(self.connection)
                self.connection.delete()
                self.connection = None
                return True
               

        return super(QNodesEditor, self).eventFilter(object, event)
