from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout

class PFSScene(QGraphicsScene):
    def __init__(self):
        super(QGraphicsScene, self).__init__()

class PFSView(QGraphicsView):
    def __init__(self, scene):
        super(QGraphicsView, self).__init__(scene)

class PFSPage(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self._file = None
        self._scene = PFSScene()
        self._view = PFSView(self._scene)
        layout = QVBoxLayout()
        layout.addWidget(self._view)
        self.setLayout(layout)
        
    def getTabName(self):
        if self._file is None:
            return "New_Model"
        return "New_Model"
    