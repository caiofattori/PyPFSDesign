from PyQt5.QtWidgets import QGraphicsItem, QColorDialog, QWidget, QDialog
from PyQt5.QtGui import QPen, QColor, QBrush, QFont, QFontMetrics, QPainter, QMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QRect, QXmlStreamWriter
from undo import PFSUndoPropertyText, PFSUndoPropertyButton, PFSUndoPropertyCombo, PFSUndoAddTag, PFSUndoRemoveTag
from dialog import PFSDialogTag
from PyQt5.QtXml import QDomNode

class PFSSenderSignal(QObject):
	changed = pyqtSignal()
	deleted = pyqtSignal()
	penEdited = pyqtSignal(object)
	def __init__(self):
		super(QObject, self).__init__()
		
class PFSTags(QWidget):
	removed = pyqtSignal(object)
	def __init__(self, name, use=""):
		QWidget.__init__(self)
		self._name = name
		self._use = use
		self._font = QFont("Serif", 8)
		self._rect = QRect(0,0,10,10)
		self._brush = QBrush(Qt.white, Qt.SolidPattern)
		
	def clone(self):
		ans = PFSTags(self._name, self._use)
		ans.removed.connect(self.removed.emit)
		return ans
	
	def simpleUse(self):
		if len(self._use) > 16:
			return self._use[:8] + "\n" + self._use[8:13] + "..."
		if len(self._use) > 8:
			return self._use[:5] + "..."
		return self._use
		
	def simpleName(self):
		if len(self._name) > 30:
			return self._name[:10] + "\n" + self._name[10:20] + "\n" + self._name[20:27] + "..."
		if len(self._name) > 20:
			return self._name[:10] + "\n" + self._name[10:17] + "..."
		if len(self._name) > 10:
			return self._name[:7] + "..."
		return self._name
		
	def updateRect(self):
		fm =QFontMetrics(self._font)
		self._useRect = fm.size(Qt.TextExpandTabs, self.simpleUse())
		self._nameRect = fm.size(Qt.TextExpandTabs, self.simpleName())
		self._rect = QRect(0,0, self._useRect.width() + self._nameRect.width()+23, max(self._useRect.height(), self._nameRect.height())+4)
		x = self._useRect.width() + self._nameRect.width() + 12
		y = self._rect.center().y() - 3
		self._closeRect = QRect(x, y, 6, 6)
		
	def paintEvent(self, ev):
		self.updateRect()
		p = QPainter(self)
		p.setBrush(self._brush)
		p.drawRoundedRect(self._rect, 10, 10)
		p.drawLine(self._useRect.width() + 6, self._rect.top(), self._useRect.width() + 6, self._rect.bottom())
		p.setFont(self._font)
		p.drawText(3, 0, self._useRect.width(), self._rect.height(), Qt.AlignCenter, self.simpleUse())
		p.drawText(self._useRect.width() + 9, 0, self._nameRect.width(), self._rect.height(), Qt.AlignCenter, self.simpleName())
		p.drawLine(self._closeRect.topLeft(), self._closeRect.bottomRight())
		p.drawLine(self._closeRect.bottomLeft(), self._closeRect.topRight())
		
	def mousePressEvent(self, ev: QMouseEvent):
		if self._closeRect.contains(ev.pos()):
			self.removed.emit(self)
	
	def __eq__(self, other):
		if not isinstance(other, PFSTags):
			return False
		return self._name == other._name and self._use == other._use

class PFSBasicElement(object):
	def __init__(self, id):
		self._id = id
		self._tags = []
		
	def addTag(self, name, use=""):
		print("x1")
		tag = PFSTags(name, use)
		print("x2")
		tag.removed.connect(self.deleteTag)
		print("x3")
		self._tags.append(tag)
		print("x4")
	
	def createTag(self, net):
		name, use, ans = PFSDialogTag.getTag()
		if ans:
			x = PFSUndoAddTag(self, name, use)
			net.undoStack.push(x)
	
	def removeTag(self, name, use):
		for tag in self._tags:
			if tag._name == name and tag._use == use:
				self._tags.remove(tag)
				return
	
	def generateXml(self, xml: QXmlStreamWriter):
		if len(self._tags) == 0:
			return
		xml.writeStartElement("tags")
		for tag in self._tags:
			xml.writeStartElement("tag")
			xml.writeAttribute("name", tag._name)
			xml.writeAttribute("use", tag._use)
			xml.writeEndElement()
		xml.writeEndElement()
		
	def createFromXml(node: QDomNode):
		ans = []
		if node.nodeName() != "tags":
			return ans
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() != "tag":
				continue
			attr = child.attributes()
			if not (child.hasAttributes() and attr.contains("name")):
				continue
			name = attr.namedItem("name").nodeValue()
			use = ""
			if attr.contains("use"):
				use = attr.namedItem("use").nodeValue()
			ans.append(PFSTags(name, use))
		return ans

class PFSElement(PFSBasicElement, QGraphicsItem):
	SELECTED_PEN = QPen(Qt.red)
	SELECTED_PEN_ALT = QPen(Qt.blue)
	PEN_LIST = {"Solida": Qt.SolidLine, "Tracejada": Qt.DashLine, "Pontilhada": Qt.DotLine}
	def __init__(self, id: str):
		PFSBasicElement.__init__(self, id)
		QGraphicsItem.__init__(self)
		self.setFlag(QGraphicsItem.ItemIsSelectable)
	
	def createTag(self):
		PFSBasicElement.createTag(self, self.scene()._page._net)
		
	def deleteTag(self, tag):
		x = PFSUndoRemoveTag(self, tag)
		self.scene()._page._net.undoStack.push(x)
	
	def removeTag(self, name, use):
		PFSBasicElement.removeTag(self, name, use)
		self.scene()._page._net.fillProperties(self.propertiesTable())
	
	def addTag(self, name, use="", update=True):
		PFSBasicElement.addTag(self, name, use)
		if update:
			self.scene()._page._net.fillProperties(self.propertiesTable())
	
	def selectSingle(self):
		self.scene()._page._net.showPage(self.scene()._page)
		self.scene().clearSelection()
		self.setSelected(True)
		self.scene()._page._net.fillProperties(self.propertiesTable())	
		
	def canDelete(self):
		return True
		
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