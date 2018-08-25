from generic import *
from xml import PFSXmlBase
from PyQt5.QtXml import QDomNode
from PyQt5.QtCore import Qt, QRectF, QXmlStreamReader, QXmlStreamWriter
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush, QPainter
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget

class PFSActivity(PFSNode):
	STANDARD_PEN = QPen(Qt.black)
	STANDARD_BRUSH = QBrush(Qt.transparent, Qt.SolidPattern)	
	def __init__(self, id: str, x: int, y: int, text: str="Atividade"):
		PFSNode.__init__(self, id, x, y)
		self._subNet= None
		self._tooltip = ""
		self._textFont = QFont("Helvetica", 15)
		self._lineNumbers = 1
		self._charsNumbers = 0
		self.setText(text)
		self._fontMetrics = QFontMetrics(self._textFont)
		self._pen = self.STANDARD_PEN
		self._brush = self.STANDARD_BRUSH
		
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("activity")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, self.sceneBoundingRect(), self._pen, self._brush)
		PFSXmlBase.text(xml, self._text, 0, 0, font=self._textFont, tag="text", align="center")
		xml.writeStartElement("tooltip")
		xml.writeCharacters(self._tooltip)
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
		tooltip = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
			if child.nodeName() == "text":
				text = PFSXmlBase.getText(child)
			if child.nodeName() == "tooltip":
				tooltip = child.nodeValue()
		if graphics is not None and text is not None:
			ac = PFSActivity(id, graphics.rect.x(), graphics.rect.y())
			ac.setText(text.annotation)
			if tooltip is not None:
				ac._tooltip = tooltip
			if text.font is not None:
				ac._textFont = text.font
			if graphics.line is not None:
				ac._pen = graphics.line
			if graphics.brush is not None:
				ac._brush = graphics.brush
			return ac			
		return None
		
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setPen(Qt.black)
		p.setFont(self._textFont)
		rect = self.sceneBoundingRect()
		p.drawText(rect, Qt.AlignCenter, self._text)
		p.drawLine(rect.left() + 1, rect.top() + 1, rect.left() + 6, rect.top() + 1)
		p.drawLine(rect.left() + 1, rect.bottom() - 1, rect.left() + 6, rect.bottom() - 1)
		p.drawLine(rect.left() + 1, rect.top() + 1, rect.left() + 1, rect.bottom() - 1)
		p.drawLine(rect.right() - 1, rect.top() + 1, rect.right() - 6, rect.top() + 1)
		p.drawLine(rect.right() - 1, rect.bottom() - 1, rect.right() - 6, rect.bottom() - 1)
		p.drawLine(rect.right() - 1, rect.top() + 1, rect.right() - 1, rect.bottom() - 1)		
		
	def setText(self, text: str):
		self._text = text
		
	def setTooltip(self, text: str):
		self._tooltip = text
		
	def boundingRect(self):
		s = self._fontMetrics.size(Qt.TextExpandTabs, self._text)
		return QRectF(self._x, self._y, s.width() + 15, s.height() + 4)
		
class PFSDistributor(PFSNode):
	STANDARD_SIZE = 20
	STANDARD_PEN = QPen(Qt.black)
	STANDARD_BRUSH = QBrush(Qt.transparent, Qt.SolidPattern)
	def __init__(self, id: str, x: int, y: int):
		PFSNode.__init__(self, id, x, y)
		self._tooltip = ""
		self._diameter = self.STANDARD_SIZE
		self._pen = self.STANDARD_PEN
		self._brush = self.STANDARD_BRUSH
		
	def setTooltip(self, text: str):
		self._tooltip = text

	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("distributor")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, self.sceneBoundingRect(), self._pen, self._brush)
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
		tooltip = None
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getNode(child)
			if child.nodeName() == "tooltip":
				tooltip = child.nodeValue()
		if graphics is not None:
			di = PFSDistributor(id, graphics.rect.x(), graphics.rect.y())
			if tooltip is not None:
				di._tooltip = tooltip
			if graphics.line is not None:
				di._pen = graphics.line
			if graphics.brush is not None:
				di._brush = graphics.brush
			return di			
		return None
	
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setPen(Qt.black)
		rect = self.sceneBoundingRect()
		p.drawEllipse(rect.left(), rect.top(), rect.width() - 2, rect.height() - 2)
	
	def boundingRect(self):
		return QRectF(self._x, self._y, self._diameter + 2, self._diameter + 2)
		
class PFSRelation(PFSElement):
	def __init__(self, id: str, source: PFSNode, target: PFSNode):
		super(PFSElement, self).__init__(id)
		self._source = source
		self._target = target
		
	def __del__(self):
		self._source.remInRelation(self)
		self._target.remOutRelation(self)
		
	def createRelation(id: str, source: PFSNode, target: PFSNode):
		if isinstance(source, PFSActivity):
			if isinstance(source, PFSDistributor):
				r = PFSRelation(id, source, target)
				if source.addInRelation(r) and target.addOutRelation(r):
					return r
		elif isinstance(source, PFSDistributor):
			if isinstance(source, PFSActivity):
				r = PFSRelation(id, source, target)
				if source.addInRelation(r) and target.addOutRelation(r):
					return r
		return None
		