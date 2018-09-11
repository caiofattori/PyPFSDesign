from PyQt5.QtWidgets import QGraphicsItem, QColorDialog
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from undo import PFSUndoPropertyText, PFSUndoPropertyButton, PFSUndoPropertyCombo

class PFSSenderSignal(QObject):
	changed = pyqtSignal()
	deleted = pyqtSignal()
	penEdited = pyqtSignal(object)
	def __init__(self):
		super(QObject, self).__init__()

class PFSElement(QGraphicsItem):
	SELECTED_PEN = QPen(Qt.red)
	SELECTED_PEN_ALT = QPen(Qt.blue)
	PEN_LIST = {"Solida": Qt.SolidLine, "Tracejada": Qt.DashLine, "Pontilhada": Qt.DotLine}
	def __init__(self, id: str):
		super(QGraphicsItem, self).__init__()
		self._id = id
		self.setFlag(QGraphicsItem.ItemIsSelectable)
	
	def selectSingle(self):
		self.scene()._page._net.showPage(self.scene()._page)
		self.scene().clearSelection()
		self.setSelected(True)
		self.scene()._page._net.fillProperties(self.propertiesTable())	
		
class PFSNode(PFSElement):
	
	def __init__(self, id: str, x: int, y: int):
		PFSElement.__init__(self, id)
		self._x = x
		self._y = y
		self._width = 0
		self._height = 0
		self._pen = QPen(Qt.black)
		self._brush = QBrush(Qt.white, Qt.SolidPattern)
		self.emitter = PFSSenderSignal()
		self.changed = self.emitter.changed
		self.deleted = self.emitter.deleted
		self.penEdited = self.emitter.penEdited
		
	def move(self, x, y):
		self._x = self._x + x
		self._y = self._y + y
		self.changed.emit()
	
	def setPenColor(self, color: QColor):
		self._pen.setColor(color)
		self.scene().update()
		
	def setPenStyle(self, style: Qt):
		self._pen.setStyle(style)
		self.scene().update()
		self.penEdited.emit(self)
		
	def setPenWidth(self, width: str):
		self._pen.setWidth(float(width))
		self.scene().update()
		
	def setBrushColor(self, color: QColor):
		self._brush.setColor(color)
		self.scene().update()
	
	def changeElementPosX(self, prop):
		x = PFSUndoPropertyText(prop, self.moveX)
		self.scene()._page._net.undoStack.push(x)

	def changeElementPosY(self, prop):
		x = PFSUndoPropertyText(prop, self.moveY)
		self.scene()._page._net.undoStack.push(x)

	def changeElementWidth(self, prop):
		x = PFSUndoPropertyText(prop, self.resizeWidth)
		self.scene()._page._net.undoStack.push(x)

	def changeElementHeight(self, prop):
		x = PFSUndoPropertyText(prop, self.resizeHeight)
		self.scene()._page._net.undoStack.push(x)
	
	def changeLineColor(self):
		color = QColorDialog.getColor(self._pen.color(), self.scene()._page._net, "Escolha a cor do contorno")
		if color.isValid() and color != self._pen.color():
			x = PFSUndoPropertyButton(color, self._pen.color(), self.setPenColor)
			self.scene()._page._net.undoStack.push(x)
			
	def changeLineStyle(self, text):
		if text in self.PEN_LIST:
			x = PFSUndoPropertyCombo(self.PEN_LIST[text], self._pen.style(), self.setPenStyle)
			self.scene()._page._net.undoStack.push(x)
	
	def changeLineWidth(self, prop):
		x = PFSUndoPropertyText(prop, self.setPenWidth)
		self.scene()._page._net.undoStack.push(x)
		
	def changeFillColor(self):
		color = QColorDialog.getColor(self._brush.color(), self.scene()._page._net, "Escolha a cor do preenchimento")
		if color.isValid() and color != self._brush.color():
			x = PFSUndoPropertyButton(color, self._brush.color(), self.setBrushColor)
			self.scene()._page._net.undoStack.push(x)
	
	def moveX(self, txt):
		self._x = float(txt)
		self.scene().update()
	
	def moveY(self, txt):
		self._y = float(txt)
		self.scene().update()	
	
	def resizeWidth(self, txt):
		self._width = float(txt)
		self.scene().update()
		
	def resizeHeight(self, txt):
		self._height = float(txt)
		self.scene().update()
	
class PFSActive(PFSNode):
	def __init__(self, id, x, y):
		PFSNode.__init__(self, id, x, y)
		
class PFSPassive(PFSNode):
	def __init__(self, id, x, y):
		PFSNode.__init__(self, id, x, y)