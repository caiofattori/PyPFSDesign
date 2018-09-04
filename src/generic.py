from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class PFSSenderSignal(QObject):
	changed = pyqtSignal()
	deleted = pyqtSignal()
	def __init__(self):
		super(QObject, self).__init__()

class PFSElement(QGraphicsItem):
	SELECTED_PEN = QPen(Qt.red)
	SELECTED_PEN_ALT = QPen(Qt.blue)
	PEN_LIST = {"Solida": Qt.SolidLine, "Tracejada": Qt.DashLine, "Pontilhada": Qt.DotLine}
	def __init__(self, id: str):
		super(QGraphicsItem, self).__init__()
		self._id = id
		
class PFSNode(QGraphicsItem):
	PEN_LIST = {"Solida": Qt.SolidLine, "Tracejada": Qt.DashLine, "Pontilhada": Qt.DotLine}
	def __init__(self, id: str, x: int, y: int):
		QGraphicsItem.__init__(self)
		self._x = x
		self._y = y
		self._id = id
		self.emitter = PFSSenderSignal()
		self.changed = self.emitter.changed
		self.deleted = self.emitter.deleted
		
	def move(self, x, y):
		self._x = self._x + x
		self._y = self._y + y
		self.changed.emit()
		