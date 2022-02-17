import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QGraphicsItem, QGraphicsView
from PyQt5.QtCore import QRectF, QPointF, pyqtSignal, QObject
from PyQt5 import QtCore

from OSMRailExport import Downloader

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi("MainGUI.ui", self)

        self.scene = QGraphicsScene()
        self.mainView.setScene(self.scene)

        # Slots einrichten
        self.ui.btnBeenden.triggered.connect(self.onBeenden)
        self.ui.btnNeu.triggered.connect(self.onNeu)
        self.ui.btnOpen.triggered.connect(self.openFileDialog)
        self.ui.btnSpeichernUnter.triggered.connect(self.saveFileDialog)
        self.ui.btnZoomIn.triggered.connect(self.onZoomIn)
        self.ui.btnZoomOut.triggered.connect(self.onZoomOut)
        self.ui.btnGesamtansicht.triggered.connect(self.onGesamtansicht)
        #self.ui.pushButton.clicked.connect(self.onBeenden)

        # Graphic View
        self.streckendarstellung()

        # Meldung in StatusBar
        self.ui.statusBar.showMessage("Hallo")

    def onBeenden(self, q):
        self.close()

    def onNeu(self):
        k = Koordinateneingabe(self)
        k.show()

    def openFileDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self)
        if fileName:
            print(fileName)

    def saveFileDialog(self):
        fileName, _ = QFileDialog.getSaveFileName(self)
        if fileName:
            print(fileName)

    def onZoomIn(self):
        self.mainView.scale(1.5,1.5)

    def onZoomOut(self):
        self.mainView.scale(2/3,2/3)

    def onGesamtansicht(self):
        pass
        
    def streckendarstellung(self):
        r = Downloader()
        bbx = r.bbxBuilder(2991396848, 389926882)
        r.downloadBoundingBox(bbx)
        
        for n in r.rn.nodes:
            #r=5
            #scene.addEllipse(-x-r, y-r, 2*r, 2*r)
            i = NodeItem(-r.rn.nodes[n].x, r.rn.nodes[n].y, r.rn.nodes[n], self)
            self.scene.addItem(i)
            

        for e in r.rn.edges:
            n1 = r.rn.edges[e]._node1
            n2 = r.rn.edges[e]._node2
            self.scene.addLine(-n1.x, n1.y, -n2.x, n2.y)
        
        

class Koordinateneingabe(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi("Koordinateneingabe.ui", self)
        self.ui.buttonBox.accepted.connect(self.onOK)

    def onOK(self):
        r = RailNetwork()
        bbx = [self.ui.lat1.text(), self.ui.lon1.text(), self.ui.lat2.text(), self.ui.lon2.text()]


class NodeItem(QGraphicsItem):
    def __init__(self, x, y, node, window, parent=None):
        super().__init__(parent)
        self._node = node
        self._x = int(x)
        self._y = int(y)
        self._window = window

        #self._selectedChange.connect(self.mousePressEvent)
        
    def boundingRect(self):
        penWidth = 1.0
        return QRectF(-10+self._x, -10 - penWidth / 2+self._y,
                      20 + penWidth, 20 + penWidth)

    def paint(self, painter, option, widget):
        #painter.drawRoundedRect(-10+self._x, -10+self._y, 20, 20, 5, 5)
        painter.drawEllipse(QPointF(self._x, self._y), 5, 5)

    def mousePressEvent(self, event):
        print(self._node.OSMId)
        self._window.ui.statusBar.showMessage("Node: " + str(self._node.OSMId))

class MyGraphicView(QGraphicsView):
    def __init__(self, parent=None):
        super(MyGraphicView,self).__init__(parent)

    





app = QtWidgets.QApplication(sys.argv)
dialog = MainWindow()
dialog.show()

sys.exit(app.exec_())
