from generic import *
from xml import PFSXmlBase
from PyQt5.QtXml import QDomNode
from PyQt5.QtCore import Qt, QRectF, QXmlStreamReader, QXmlStreamWriter, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush, QPainter, QPainterPath, QPolygon, QPolygonF, QColor, QIcon
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget, QFontDialog, QColorDialog, QTreeWidgetItem
import math
from table import *
from undo import PFSUndoPropertyText, PFSUndoPropertyButton, PFSUndoPropertyCombo
from image import PFSDistributorIcon, PFSActivityIcon, PFSRelationIcon, PFSOpenActivityIcon, PFSCloseActivityIcon
from tree import PFSTreeItem

class PFSAux:
	def __init__(self):
		pass

class PFSActivityContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._text = None
		self._width = None
		self._height = None
		self._textFont = None
		self._fontMetrics = None
		self._pen = None
		self._brush = None

class PFSActivity(PFSActive):
	def __init__(self, id: str, x: int, y: int, text: str="Atividade"):
		PFSActive.__init__(self, id, x, y)
		self._subPage = None
		self._textFont = QFont("Helvetica", 15)
		self.setText(text)
		self._fontMetrics = QFontMetrics(self._textFont)
		self._minWidth = 0
		self._minHeight = 0
		self.minimunRect()
		self._width = self._minWidth
		self._height = self._minHeight
		self.addTag("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "aaaaaaaaaaaaaaaaaaaaa")
		
	def copy(self, x, y):
		ans = PFSActivityContent()
		ans._x = self._x - x
		ans._y = self._y - y
		ans._text = self._text
		ans._width = self._width
		ans._height = self._height
		ans._textFont = self._textFont
		ans._fontMetrics = self._fontMetrics
		ans._pen = self._pen
		ans._brush = self._brush
		return ans
	
	def paste(content, id, dx, dy):
		ans = PFSActivity(id, content._x + dx, content._y + dy, content._text)
		ans._width = content._width
		ans._height = content._height
		ans._textFont = content._textFont
		ans._fontMetrics = content._fontMetrics
		ans._pen = content._pen
		ans._brush = content._brush
		return ans
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		if self._subPage is not None:
			child = self._subPage.tree(tree)		
		return tree
	
	def simpleTree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def hasSubPage(self):
		return self._subPage is not None
	
	def setSubPage(self, page):
		if self._subPage is not None:
			return False
		self._subPage = page
		return True
	
	def removeSubPage(self):
		self._subPage = None
	
	def subPage(self):
		return self._subPage
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("activity")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, QRectF(self._x, self._y, self._width, self._height), self._pen, self._brush)
		PFSXmlBase.text(xml, self._text, 0, 0, font=self._textFont, tag="text", align="center")
		xml.writeEndElement()
		xml.writeEndElement() #fecha activity
		PFSXmlBase.close(xml)
	
	def createFromXml(node: QDomNode):
		if node.nodeName() != "activity":
			return None
		if not (node.hasAttributes() and node.attributes().contains("id")):
			return None
		id = node.attributes().namedItem("id").nodeValue()
		childs = node.childNodes()
		graphics = None
		text = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
			if child.nodeName() == "text":
				text = PFSXmlBase.getText(child)
		if graphics is not None and text is not None:
			ac = PFSActivity(id, graphics.rect.x(), graphics.rect.y())
			ac._width = graphics.rect.width()
			ac._height = graphics.rect.height()
			ac.setText(text.annotation)
			if text.font is not None:
				ac._textFont = text.font
				ac._fontMetrics = QFontMetrics(text.font)
			if graphics.line is not None:
				ac._pen = graphics.line
			if graphics.brush is not None:
				ac._brush = graphics.brush
			return ac
		return None
		
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setPen(Qt.NoPen)
		p.setBrush(self._brush)
		rect = self.sceneBoundingRect()
		p.drawRect(self._x, self._y, self._width, self._height)
		p.setPen(self._pen)
		p.setFont(self._textFont)
		p.drawText(rect, Qt.AlignCenter, self._text)
		p.save()
		if self.isSelected():
			if self._pen.color() == PFSElement.SELECTED_PEN:
				p.setPen(PFSElement.SELECTED_PEN_ALT)
			else:
				p.setPen(PFSElement.SELECTED_PEN)
		p.drawLine(self._x, self._y, self._x + 6, self._y)
		p.drawLine(self._x, self._y + self._height, self._x + 6, self._y + self._height)
		p.drawLine(self._x, self._y, self._x, self._y + self._height)
		p.drawLine(self._x + self._width, self._y, self._x + self._width - 6, self._y)
		p.drawLine(self._x + self._width, self._y + self._height, self._x + self._width - 6, self._y + self._height)
		p.drawLine(self._x + self._width, self._y, self._x + self._width, self._y + self._height)		
		p.restore()
		
	def setText(self, text: str):
		self._text = text
		if self.scene() is not None:
			self.scene().update()
			self.changed.emit()
			
	def setFont(self, font: QFont):
		self._textFont = font
		self._fontMetrics = QFontMetrics(font)
		self.scene().update()
	
	def getText(self):
		return self._text
		
	def minimunRect(self):
		s = self._fontMetrics.size(Qt.TextExpandTabs, self._text)
		self._minWidth = s.width() + 15
		self._minHeight = s.height() + 4
		return QRectF(self._x, self._y, self._minWidth, self._minHeight)
	
	def boundingRect(self):
		r = self.minimunRect()
		width = max(self._width,r.width()) 
		height = max(self._height,r.height())
		return QRectF(self._x, self._y, width, height)
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		if p.x() > self._x + self._width/2:
			x = self._x + self._width
		else:
			x = self._x
		y = p.y()
		if p.y() < self._y:
			y = self._y
		elif p.y() > self._y + self._height:
			y = self._y + self._height
		return QPoint(x, y)
	
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Atividade")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição X")
		lblValue = PFSTableValueText(str(self._x))
		lblValue.edited.connect(self.changeElementPosX)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição Y")
		lblValue = PFSTableValueText(str(self._y))
		lblValue.edited.connect(self.changeElementPosY)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Largura")
		lblValue = PFSTableValueText(str(self._width))
		lblValue.edited.connect(self.changeElementWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableValueText(str(self._height))
		lblValue.edited.connect(self.changeElementHeight)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Texto")
		lblValue = PFSTableValueText(self._text)
		lblValue.edited.connect(self.changeText)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Fonte")
		lblValue = PFSTableValueButton(self._textFont.toString())
		lblValue.clicked.connect(self.changeFont)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do contorno")
		lblValue = PFSTableValueButton(self._pen.color().name())
		lblValue.clicked.connect(self.changeLineColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Linha do contorno")
		lblValue = PFSTableValueCombo(self.PEN_LIST, self._pen.style())
		self.penEdited.connect(lblValue.updateText)
		lblValue.currentTextChanged.connect(self.changeLineStyle)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Espessura do contorno")
		lblValue = PFSTableValueText(str(self._pen.width()))
		lblValue.edited.connect(self.changeLineWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do preenchimento")
		lblValue = PFSTableValueButton(self._brush.color().name())
		lblValue.clicked.connect(self.changeFillColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabelTags("Tags")
		lblValue = PFSTableValueBox(self._tags)
		ans.append([lblType, lblValue])		
		return ans
	
	def changeText(self, prop):
		x = PFSUndoPropertyText(prop, self.setText)
		self.scene()._page._net.undoStack.push(x)
		
	def changeFont(self):
		font, ans = QFontDialog.getFont(self._textFont, self.scene()._page._net, "Escolha a fonte do texto")
		if ans:
			x = PFSUndoPropertyButton(font, self._textFont, self.setFont)
			self.scene()._page._net.undoStack.push(x)
	
	def changeElementWidth(self, prop):
		if float(prop.text()) > self._minWidth:
			x = PFSUndoPropertyText(prop, self.resizeWidth)
			self.scene()._page._net.undoStack.push(x)

	def changeElementHeight(self, prop):
		if float(prop.text()) > self._minHeight:
			x = PFSUndoPropertyText(prop, self.resizeHeight)
			self.scene()._page._net.undoStack.push(x)	
	
class PFSOpenActivity(PFSActive):
	def __init__(self, id, x, y, h):
		PFSActive.__init__(self, id, x, y)
		self._h = h
		self.setFlag(QGraphicsItem.ItemIsSelectable)
	
	def canDelete(self):
		return False
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSOpenActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def simpleTree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSOpenActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def boundingRect(self):
		return QRectF(self._x-3, self._y-3, 12, self._h+3)
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("openactivity")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, QRectF(self._x, self._y, 6, self._h), self.scene()._page._subRef._pen, None)
		xml.writeEndElement() #fecha openactivity
		PFSXmlBase.close(xml)
		
	def createFromXml(node: QDomNode):
		if node.nodeName() != "openactivity":
			return None
		if not (node.hasAttributes() and node.attributes().contains("id")):
			return None
		id = node.attributes().namedItem("id").nodeValue()
		childs = node.childNodes()
		graphics = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
		if graphics is not None:
			oa = PFSOpenActivity(id, graphics.rect.x(), graphics.rect.y(), graphics.rect.height())
			return oa
		return None	
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		y = p.y()
		if p.y() < self._y + 5:
			y = self._y + 5
		elif p.y() > self._y + self._h - 5:
			y = self._y + self._h - 5
		return QPoint(self._x, y)
		
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		ref = self.scene()._page._subRef
		p.setPen(ref._pen)
		p.save()
		if self.isSelected():
			if ref._pen.color() == PFSElement.SELECTED_PEN:
				p.setPen(PFSElement.SELECTED_PEN_ALT)
			else:
				p.setPen(PFSElement.SELECTED_PEN)
		p.drawLine(self._x, self._y, self._x + 6, self._y)
		p.drawLine(self._x, self._y + self._h, self._x + 6, self._y + self._h)
		p.drawLine(self._x, self._y, self._x, self._y + self._h)
		p.restore()
		
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Atividade")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição X")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().x()))
		lblValue.edited.connect(self.changeElementPosX)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição Y")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().y()))
		lblValue.edited.connect(self.changeElementPosY)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().height()))
		lblValue.edited.connect(self.changeElementHeight)
		ans.append([lblType, lblValue])
		return ans
	
	def changeElementPosX(self, prop):
		x = PFSUndoPropertyText(prop, self.moveX)
		self.scene()._page._net.undoStack.push(x)

	def changeElementPosY(self, prop):
		x = PFSUndoPropertyText(prop, self.moveY)
		self.scene()._page._net.undoStack.push(x)

	def changeElementHeight(self, prop):
		if float(prop.text()) > self._minHeight:
			x = PFSUndoPropertyText(prop, self.resizeHeight)
			self.scene()._page._net.undoStack.push(x)

	def moveX(self, txt):
		self._x = float(txt)
		self.scene().update()

	def moveY(self, txt):
		self._y = float(txt)
		self.scene().update()

	def resizeHeight(self, txt):
		self._height = float(txt)
		self.scene().update()
		
class PFSCloseActivity(PFSActive):
	def __init__(self, id, x, y, h):
		PFSActive.__init__(self, id, x, y)
		self._h = h
		self.setFlag(QGraphicsItem.ItemIsSelectable)
	
	def canDelete(self):
		return False
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSCloseActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def simpleTree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSCloseActivityIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree	
	
	def boundingRect(self):
		return QRectF(self._x-9, self._y-3, 12, self._h+3)
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("closeactivity")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, QRectF(self._x-6, self._y, 6, self._h), self.scene()._page._subRef._pen, None)
		xml.writeEndElement() #fecha closeactivity
		PFSXmlBase.close(xml)
		
	def createFromXml(node: QDomNode):
		if node.nodeName() != "closeactivity":
			return None
		if not (node.hasAttributes() and node.attributes().contains("id")):
			return None
		id = node.attributes().namedItem("id").nodeValue()
		childs = node.childNodes()
		graphics = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
		if graphics is not None:
			return PFSCloseActivity(id, graphics.rect.x(), graphics.rect.y(), graphics.rect.height())
		return None	
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		y = p.y()
		if p.y() < self._y + 5:
			y = self._y + 5
		elif p.y() > self._y + self._h - 5:
			y = self._h - 5
		return QPoint(self._x, y)
		
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		ref = self.scene()._page._subRef
		p.setPen(ref._pen)
		p.save()
		if self.isSelected():
			if ref._pen.color() == PFSElement.SELECTED_PEN:
				p.setPen(PFSElement.SELECTED_PEN_ALT)
			else:
				p.setPen(PFSElement.SELECTED_PEN)
		p.drawLine(self._x, self._y, self._x - 6, self._y)
		p.drawLine(self._x, self._y + self._h, self._x - 6, self._y + self._h)
		p.drawLine(self._x, self._y, self._x, self._y + self._h)
		p.restore()
		
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Fecha atividade")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição X")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().x()))
		lblValue.edited.connect(self.changeElementPosX)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição Y")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().y()))
		lblValue.edited.connect(self.changeElementPosY)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableValueText(str(self.sceneBoundingRect().height()))
		lblValue.edited.connect(self.changeElementHeight)
		ans.append([lblType, lblValue])
		return ans
	
	def changeElementPosX(self, prop):
		x = PFSUndoPropertyText(prop, self.moveX)
		self.scene()._page._net.undoStack.push(x)

	def changeElementPosY(self, prop):
		x = PFSUndoPropertyText(prop, self.moveY)
		self.scene()._page._net.undoStack.push(x)

	def changeElementHeight(self, prop):
		if float(prop.text()) > self._minHeight:
			x = PFSUndoPropertyText(prop, self.resizeHeight)
			self.scene()._page._net.undoStack.push(x)

	def moveX(self, txt):
		self._x = float(txt)
		self.scene().update()

	def moveY(self, txt):
		self._y = float(txt)
		self.scene().update()

	def resizeHeight(self, txt):
		self._height = float(txt)
		self.scene().update()

class PFSDistributorContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._width = None
		self._height = None
		self._pen = None
		self._brush = None

class PFSDistributor(PFSPassive):
	STANDARD_SIZE = 20
	def __init__(self, id: str, x: int, y: int):
		PFSPassive.__init__(self, id, x, y)
		self._width = self.STANDARD_SIZE
		self._height = self.STANDARD_SIZE
	
	def hasSubPage(self):
		return False
		
	def copy(self, x, y):
		ans = PFSDistributorContent()
		ans._x = self._x - x
		ans._y = self._y - y
		ans._width = self._width
		ans._height = self._height
		ans._pen = self._pen
		ans._brush = self._brush
		return ans
	
	def paste(content, id, dx, dy):
		ans = PFSDistributor(id, content._x + dx, content._y + dy)
		ans._width = content._width
		ans._height = content._height
		ans._pen = content._pen
		ans._brush = content._brush
		return ans	
		
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSDistributorIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def simpleTree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSDistributorIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree

	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("distributor")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, QRectF(self._x, self._y, self._width, self._height), self._pen, self._brush)
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)
	
	def createFromXml(node: QDomNode):
		if node.nodeName() != "distributor":
			return None
		if not (node.hasAttributes() and node.attributes().contains("id")):
			return None
		id = node.attributes().namedItem("id").nodeValue()
		childs = node.childNodes()
		graphics = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
		if graphics is not None:
			di = PFSDistributor(id, graphics.rect.x(), graphics.rect.y())
			di._width = graphics.rect.width()
			di._height = graphics.rect.height()
			if graphics.line is not None:
				di._pen = graphics.line
			if graphics.brush is not None:
				di._brush = graphics.brush
			return di			
		return None
	
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setBrush(self._brush)
		p.setPen(self._pen)
		if self.isSelected():
			if self._brush.color() == PFSElement.SELECTED_PEN:
				p.setPen(PFSElement.SELECTED_PEN_ALT)
			else:
				p.setPen(PFSElement.SELECTED_PEN)
		p.drawEllipse(self._x, self._y, self._width, self._height)
	
	def boundingRect(self):
		return QRectF(self._x, self._y, self._width + 2, self._height + 2)
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		x = self._x + self._width/2
		y = self._y + self._height/2
		ang = math.atan2(p.y()-y, p.x()-x)
		return QPoint(math.cos(ang)*self._width/2 + x, math.sin(ang)*self._height/2 + y)
	
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Atividade")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição X")
		lblValue = PFSTableValueText(str(self._x))
		lblValue.edited.connect(self.changeElementPosX)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição Y")
		lblValue = PFSTableValueText(str(self._y))
		lblValue.edited.connect(self.changeElementPosY)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Largura")
		lblValue = PFSTableValueText(str(self._width))
		lblValue.edited.connect(self.changeElementWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableValueText(str(self._height))
		lblValue.edited.connect(self.changeElementHeight)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do contorno")
		lblValue = PFSTableValueButton(self._pen.color().name())
		lblValue.clicked.connect(self.changeLineColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Linha do contorno")
		lblValue = PFSTableValueCombo(self.PEN_LIST, self._pen.style())
		self.penEdited.connect(lblValue.updateText)
		lblValue.currentTextChanged.connect(self.changeLineStyle)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Espessura do contorno")
		lblValue = PFSTableValueText(str(self._pen.width()))
		lblValue.edited.connect(self.changeLineWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do preenchimento")
		lblValue = PFSTableValueButton(self._brush.color().name())
		lblValue.clicked.connect(self.changeFillColor)
		ans.append([lblType, lblValue])
		return ans	

class PFSGraphItems(QObject):
	penEdited = pyqtSignal(object)
	def __init__(self):
		QObject.__init__(self)

class PFSRelation(PFSElement):
	def __init__(self, id: str, source: PFSNode, target: PFSNode):
		PFSElement.__init__(self,id)
		self._source = source
		self._target = target
		self._midPoints = []
		self._firstPoint = None
		self._lastPoint = None
		self.updatePoints()
		self._pen = QPen(Qt.black)
		self._obj = PFSGraphItems()
		self.penEdited = self._obj.penEdited
	
	def simpleTree(self, parent):
		return QTreeWidgetItem(parent, ["Relação " + self._id], 0)
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSRelationIcon()))
		tree.clicked.connect(self.selectSingle)	
		child = self._source.simpleTree(tree)
		child = self._target.simpleTree(tree)
		return tree
	
	def hasSubPage(self):
		return False
	
	def createRelation(id: str, source: PFSNode, target: PFSNode):
		if isinstance(source, PFSActive):
			if isinstance(target, PFSPassive):
				r = PFSRelation(id, source, target)
				source.changed.connect(r.updatePoints)
				target.changed.connect(r.updatePoints)
				source.deleted.connect(r.putInDelete)
				target.deleted.connect(r.putInDelete)
				return r
		elif isinstance(source, PFSPassive):
			if isinstance(target, PFSActive):
				r = PFSRelation(id, source, target)
				source.changed.connect(r.updatePoints)
				target.changed.connect(r.updatePoints)
				source.deleted.connect(r.putInDelete)
				target.deleted.connect(r.putInDelete)
				return r
		return None
	
	def updatePoints(self):
		if len(self._midPoints) == 0:
			if isinstance(self._source, PFSActivity):
				self._firstPoint = self._source.getBestRelationPoint(self._target.sceneBoundingRect().center())
				self._lastPoint = self._target.getBestRelationPoint(self._firstPoint)
			else:
				self._lastPoint = self._target.getBestRelationPoint(self._source.sceneBoundingRect().center())
				self._firstPoint = self._source.getBestRelationPoint(self._lastPoint)
		else:
			self._firstPoint = self._source.getBestRelationPoint(self._midPoints[0])
			self._lastPoint = self._target.getBestRelationPoint(self._midPoints[-1])
	
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setPen(self._pen)
		if self.isSelected():
			if self._pen.color() == PFSElement.SELECTED_PEN:
				p.setPen(PFSElement.SELECTED_PEN_ALT)
			else:
				p.setPen(PFSElement.SELECTED_PEN)
		lastPoint = self._firstPoint
		for point in self._midPoints:
			p.drawLine(lastPoint, point)
			lastPoint = point
		p.drawLine(lastPoint, self._lastPoint)
		ang = math.atan2(self._lastPoint.y()-lastPoint.y(), self._lastPoint.x()-lastPoint.x())
		p.save()
		p.translate(self._lastPoint)
		p.rotate(ang*180/math.pi)
		self.drawArrow(p)
		p.restore()
	
	def drawArrow(self, p:QPainter):
		p.drawLine(-10, -6, 0, 0)
		p.drawLine(-10, 6, 0, 0)
	
	def boundingRect(self):
		t = min(self._firstPoint.y(),self._lastPoint.y())
		b = max(self._firstPoint.y(),self._lastPoint.y())
		l = min(self._firstPoint.x(),self._lastPoint.x())
		r = max(self._firstPoint.x(),self._lastPoint.x())
		for p in self._midPoints:
			if p.x() < l:
				l = p.x()
			if p.x() > r:
				r = p.x()
			if p.y() < t:
				t = p.y()
			if p.y() > b:
				b = p.y()
		return QRectF(l, t, r-l, b-t)
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("relation")
		xml.writeAttribute("id", self._id)
		xml.writeAttribute("source", self._source._id)
		xml.writeAttribute("target", self._target._id)
		PFSXmlBase.graphicsArc(xml, self._midPoints, self._pen)
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)
		
	def move(self, x, y):
		delta = QPoint(x, y)
		for p in self._midPoints:
			p += delta
	
	def createFromXml(node: QDomNode):
		if node.nodeName() != "relation":
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("id")):
			return None
		id = attr.namedItem("id").nodeValue()
		if not (attr.contains("source") and attr.contains("target")):
			return None
		source = attr.namedItem("source").nodeValue()
		target = attr.namedItem("target").nodeValue()
		graphics = None
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getArc(child)
		re = PFSAux()
		re.id = id
		re.source = source
		re.target = target
		if graphics is not None and graphics.line is not None:
			re.pen = graphics.line
		else:
			re.pen = None
		if graphics is not None and graphics.pos is not None:
			re.midPoints = graphics.pos
		else:
			re.midPoints = []
		return re
	
	def shape(self) -> QPainterPath:
		path = QPainterPath()
		p = QPolygon()
		p.append(self._firstPoint)
		for m in self._midPoints:
			p.append(m)
		p.append(self._lastPoint)
		p.translate(0, -5)
		n = p.count()
		finalPolygon = QPolygonF()
		finalPolygon.append(self._firstPoint)
		for i in range(n):
			finalPolygon.append(p.point(i))
		finalPolygon.append(self._lastPoint)
		p.translate(0, 10)
		for i in range(n):
			finalPolygon.append(p.point(n-i-1))
		finalPolygon.append(self._firstPoint)
		path.addPolygon(finalPolygon)
		return path
		
	def putInDelete(self):
		if self.scene() is not None:
			lst = self.scene()._itemsDeleted
			if self not in lst:
				lst.append(self)
	
	def setPenColor(self, color: QColor):
		self._pen.setColor(color)
		self.scene().update()
		
	def setPenStyle(self, style: Qt):
		self._pen.setStyle(style)
		self.scene().update()
		self.penEdited.emit(style)
		
	def setPenWidth(self, width: str):
		self._pen.setWidth(float(width))
		self.scene().update()	
	
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Arco")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do contorno")
		lblValue = PFSTableValueButton(self._pen.color().name())
		lblValue.clicked.connect(self.changeLineColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Linha do contorno")
		lblValue = PFSTableValueCombo(self.PEN_LIST, self._pen.style())
		self.penEdited.connect(lblValue.updateText)
		lblValue.currentTextChanged.connect(self.changeLineStyle)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Espessura do contorno")
		lblValue = PFSTableValueText(str(self._pen.width()))
		lblValue.edited.connect(self.changeLineWidth)
		ans.append([lblType, lblValue])
		return ans
	
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