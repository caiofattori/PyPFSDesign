from generic import *
from xml import PFSXmlBase
from PyQt5.QtXml import QDomNode
from PyQt5.QtCore import Qt, QRectF, QXmlStreamReader, QXmlStreamWriter, QPoint
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush, QPainter, QPainterPath, QPolygon, QPolygonF
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget
import math

class PFSAux:
	def __init__(self):
		pass

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
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		
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
		p.save()
		if self.isSelected():
			p.setPen(PFSElement.SELECTED_PEN)
		p.drawLine(rect.left() + 1, rect.top() + 1, rect.left() + 6, rect.top() + 1)
		p.drawLine(rect.left() + 1, rect.bottom() - 1, rect.left() + 6, rect.bottom() - 1)
		p.drawLine(rect.left() + 1, rect.top() + 1, rect.left() + 1, rect.bottom() - 1)
		p.drawLine(rect.right() - 1, rect.top() + 1, rect.right() - 6, rect.top() + 1)
		p.drawLine(rect.right() - 1, rect.bottom() - 1, rect.right() - 6, rect.bottom() - 1)
		p.drawLine(rect.right() - 1, rect.top() + 1, rect.right() - 1, rect.bottom() - 1)		
		p.restore()
		
	def setText(self, text: str):
		self._text = text
		
	def setTooltip(self, text: str):
		self._tooltip = text
		
	def boundingRect(self):
		s = self._fontMetrics.size(Qt.TextExpandTabs, self._text)
		return QRectF(self._x, self._y, s.width() + 15, s.height() + 4)
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		b = self.sceneBoundingRect()
		if p.x() > b.center().x():
			x = b.right()
		else:
			x = b.left()
		y = p.y()
		if p.y() < b.top():
			y = b.top()
		elif p.y() > b.bottom():
			y = b.bottom()
		return QPoint(x, y)	
		
class PFSDistributor(PFSNode):
	STANDARD_SIZE = 20
	STANDARD_PEN = QPen(Qt.black)
	STANDARD_BRUSH = QBrush(Qt.transparent, Qt.SolidPattern)
	def __init__(self, id: str, x: int, y: int):
		PFSNode.__init__(self, id, x, y)
		self._tooltip = ""
		self._diameterX = self.STANDARD_SIZE
		self._diameterY = self.STANDARD_SIZE
		self._pen = self.STANDARD_PEN
		self._brush = self.STANDARD_BRUSH
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		
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
		if self.isSelected():
			p.setPen(PFSElement.SELECTED_PEN)
		else:
			p.setPen(Qt.black)
		rect = self.sceneBoundingRect()
		p.drawEllipse(rect.left(), rect.top(), rect.width() - 2, rect.height() - 2)
	
	def boundingRect(self):
		return QRectF(self._x, self._y, self._diameterX + 2, self._diameterY + 2)
	
	def getBestRelationPoint(self, p: QPoint) -> QPoint:
		c = self.sceneBoundingRect().center()
		ang = math.atan2(p.y()-c.y(), p.x()-c.x())
		return QPoint(self._diameterX/2*math.cos(ang) + c.x(), self._diameterY/2*math.sin(ang) + c.y())
		
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
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		
	def __del__(self):
		self._source.remInRelation(self)
		self._target.remOutRelation(self)
		
	def createRelation(id: str, source: PFSNode, target: PFSNode):
		if isinstance(source, PFSActivity):
			if isinstance(target, PFSDistributor):
				r = PFSRelation(id, source, target)
				if source.addInRelation(r) and target.addOutRelation(r):
					return r
		elif isinstance(source, PFSDistributor):
			if isinstance(target, PFSActivity):
				r = PFSRelation(id, source, target)
				if source.addInRelation(r) and target.addOutRelation(r):
					return r
		return None
	
	def updatePoints(self):
		if len(self._midPoints) == 0:
			self._firstPoint = self._source.getBestRelationPoint(self._target.sceneBoundingRect().center())
			self._lastPoint = self._target.getBestRelationPoint(self._source.sceneBoundingRect().center())
		else:
			self._firstPoint = self._source.getBestRelationPoint(self._midPoints[0])
			self._lastPoint = self._target.getBestRelationPoint(self._midPoints[-1])
	
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		if self.isSelected():
			p.setPen(PFSElement.SELECTED_PEN)
		else:
			p.setPen(Qt.black)
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
		