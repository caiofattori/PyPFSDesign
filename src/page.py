from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QPoint

class PFSScene(QGraphicsScene):
    DELTA = 20.0
    def __init__(self, w, h):
        super(QGraphicsScene, self).__init__()
        self._backgroundPoints = []
        self.resize(w,h)
        
    def resize(self, w, h):
        self.setSceneRect(0, 0, w, h)
        sx = int(w/self.DELTA - 1)
        sy = int(h/self.DELTA - 1)
        self._backgroundPoints = [QPoint((i+0.5)*self.DELTA, (j+0.5)*self.DELTA) for i in range(sx) for j in range(sy)]
        self.update()
    
    def drawBackground(self, p, r):
        p.setPen(Qt.SolidLine)
        for point in self._backgroundPoints:
            p.drawPoint(point)

class PFSView(QGraphicsView):
    def __init__(self, scene):
        super(QGraphicsView, self).__init__(scene)

class PFSPage(QWidget):
    def __init__(self, w, h):
        super(QWidget, self).__init__()
        self._file = None
        self._scene = PFSScene(w, h)
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
        layout.addLayout(layoutH)
        layout.addWidget(self._view)
        self.setLayout(layout)
        
    def resizeScene(self):
        self._scene.resize(int(self.txtWidth.text()), int(self.txtHeight.text()))
    
    def getTabName(self):
        if self._file is None:
            return "New_Model"
        return "New_Model"
    
    def newPage():
        return PFSPage(4000, 4000)