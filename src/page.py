from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from element import PFSActivity, PFSDistributor
from xml import PFSXmlBase

class PFSScene(QGraphicsScene):
    DELTA = 20.0
    inserted = pyqtSignal()
    def __init__(self, w, h, parentState):
        super(QGraphicsScene, self).__init__()
        self._backgroundPoints = []
        self.resize(w,h)
        self._paintGrid = True
        self._parentState = parentState
        self._distributorId = 0
        self._activityId = 0
        self._relationId = 0
        
    def getNewDistributorId(self):
        ans = "D" + str(self._distributorId)
        self._distributorId = self._distributorId + 1
        return ans
    
    def getNewActivityId(self):
        ans = "A" + str(self._activityId)
        self._activityId = self._activityId + 1
        return ans    
        
    def setPaintGrid(self, v = True):
        self._paintGrid = v
        self.update()
        
    def resize(self, w, h):
        self.setSceneRect(0, 0, w, h)
        sx = int(w/self.DELTA - 1)
        sy = int(h/self.DELTA - 1)
        self._backgroundPoints = [QPoint((i+0.5)*self.DELTA, (j+0.5)*self.DELTA) for i in range(sx) for j in range(sy)]
        self.update()
        
    def mousePressEvent(self, ev):
        if self._parentState._sDistributor:
            pos = ev.scenePos()
            self.addItem(PFSDistributor(self.getNewDistributorId(), pos.x(), pos.y()))
            self.inserted.emit()
            #self._parentState._sdistributor = False
        if self._parentState._sActivity:
            pos = ev.scenePos()
            self.addItem(PFSActivity(self.getNewActivityId(), pos.x(), pos.y(), "Activity"))
            self.inserted.emit()
            #self._parentState._sactivity = False        
    
    def drawBackground(self, p, r):
        if not self._paintGrid:
            return
        p.setPen(Qt.SolidLine)
        for point in self._backgroundPoints:
            p.drawPoint(point)

class PFSView(QGraphicsView):
    def __init__(self, scene):
        super(QGraphicsView, self).__init__(scene)

class PFSPage(QWidget):
    def __init__(self, w, h, stateMachine):
        super(QWidget, self).__init__()
        self._file = None
        self._scene = PFSScene(w, h, stateMachine)
        self._view = PFSView(self._scene)
        layout = QVBoxLayout()
        layoutH = QHBoxLayout()
        lblWidth = QLabel("Width: ")
        layoutH.addWidget(lblWidth)
        self.txtWidth = QLineEdit(str(w))
        self.txtWidth.editingFinished.connect(self.resizeScene)
        layoutH.addWidget(self.txtWidth)
        lblHeight = QLabel("Height: ")
        layoutH.addWidget(lblHeight)
        self.txtHeight = QLineEdit(str(h))
        self.txtHeight.editingFinished.connect(self.resizeScene)
        layoutH.addWidget(self.txtHeight)
        chkPaintGrid = QCheckBox("Show grid")
        chkPaintGrid.setChecked(True)
        chkPaintGrid.stateChanged.connect(self._scene.setPaintGrid)
        layoutH.addWidget(chkPaintGrid)
        layout.addLayout(layoutH)
        layout.addWidget(self._view)
        self.setLayout(layout)
        self._sdistributor = False
        
    def generateXml(self, xml):
        xml.writeStartElement("page")
        PFSXmlBase.open(xml)
        xml.writeStartElement("pagetype")
        xml.writeAttribute("mainpage", "true")
        xml.writeAttribute("id", "pg0")
        xml.writeAttribute("ref", "")
        xml.writeEndElement() #fim da pagetype
        xml.writeStartElement("pagegraphics")
        PFSXmlBase.position(xml, self.txtWidth.text(), self.txtHeight.text(), "dimension")
        xml.writeEndElement() #fim da pagegraphics
        PFSXmlBase.close(xml)
        for e in self._scene.items():
            if isinstance(e, PFSActivity) or isinstance(e, PFSDistributor):
                e.generateXml(xml)
        xml.writeEndElement() #fim da page
        
    def resizeScene(self):
        self._scene.resize(int(self.txtWidth.text()), int(self.txtHeight.text()))
    
    def getTabName(self):
        if self._file is None:
            return "New_Model"
        return "New_Model"
    
    def newPage(sm):
        return PFSPage(4000, 4000, sm)