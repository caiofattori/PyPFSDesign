from generic import *
from xml import PFSXmlBase
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush

class PFSActivity(PFSNode):
	STANDARD_PEN = QPen(Qt.black)
	STANDARD_BRUSH = QBrush(Qt.transparent, Qt.SolidPattern)	
	def __init__(self, id, x, y, text="Atividade"):
		PFSNode.__init__(self, id, x, y)
		self._subNet = None
		self._tooltip = ""
		self._textFont = QFont("Helvetica", 15)
		self._lineNumbers = 1
		self._charsNumbers = 0
		self.setText(text)
		self._fontMetrics = QFontMetrics(self._textFont)
		self._pen = self.STANDARD_PEN
		self._brush = self.STANDARD_BRUSH
		
	def generateXml(self, xml):
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
		
	def createFromXml(xml):
		id = xml.attributes().value("id")
		rect = None
		pen = None
		brush = None
		font = None
		text = None
		tooltip = None
		while xml.name() in ["text", "tooltip", "graphics"]:
			if xml.name() == "tooltip":
				tooltip = xml.getCharacters()
			elif xml.name() == "text":
				val = PFSXmlBase.getText(xml)
				if val is not None:
					font = val.font
					text = val.text
			else:
				val = PFSXmlBase.getNode(xml)
				if val is not None:
					rect = val.rect
					pen = val.pen
					brush = val.brush
			xml.readNextStartElement()
		if id is None or text is None or rect is None:
			return None
		ac = PFSActivity(id, rect.x(), rect.y())
		ac.setText(text)
		if tooltip is not None:
			ac._tooltip = tooltip
		if font is not None:
			ac._textFont = font
		if pen is not None:
			ac._pen = pen
		if brush is not None:
			ac._brush = brush
		return ac
		
	def paint(self, p, o, w):
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
		
	def setText(self, text):
		self._text = text
		
	def setTooltip(self, text):
		self._tooltip = text
		
	def boundingRect(self):
		s = self._fontMetrics.size(Qt.TextExpandTabs, self._text)
		return QRectF(self._x, self._y, s.width() + 15, s.height() + 4)
		
class PFSDistributor(PFSNode):
	STANDARD_SIZE = 20
	STANDARD_PEN = QPen(Qt.black)
	STANDARD_BRUSH = QBrush(Qt.transparent, Qt.SolidPattern)
	def __init__(self, id, x, y):
		PFSNode.__init__(self, id, x, y)
		self._tooltip = ""
		self._diameter = self.STANDARD_SIZE
		self._pen = self.STANDARD_PEN
		self._brush = self.STANDARD_BRUSH
		
	def setTooltip(self, text):
		self._tooltip = text

	def generateXml(self, xml):
		PFSXmlBase.open(xml)
		xml.writeStartElement("distributor")
		xml.writeAttribute("id", self._id)
		PFSXmlBase.graphicsNode(xml, self.sceneBoundingRect(), self._pen, self._brush)
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)
		
	def createFromXml(xml):
		id = xml.attributes().value("id")
		rect = None
		pen = None
		brush = None
		tooltip = None
		while xml.name() in [ "tooltip", "graphics"]:
			if xml.name() == "tooltip":
				tooltip = xml.getCharacters()
			else:
				val = PFSXmlBase.getNode(xml)
				if val is not None:
					rect = val.rect
					pen = val.pen
					brush = val.brush
			xml.readNextStartElement()
		if id is None or rect is None:
			return None
		di = PFSDistributor(id, rect.x(), rect.y())
		di._diameterX = rect.width()
		di._diameterY = rect.height()
		if tooltip is not None:
			di._tooltip = tooltip
		if pen is not None:
			di._pen = pen
		if brush is not None:
			di._brush = brush
		return di
	
	def paint(self, p, o, w):
		p.setPen(Qt.black)
		rect = self.sceneBoundingRect()
		p.drawEllipse(rect.left(), rect.top(), rect.width() - 2, rect.height() - 2)
	
	def boundingRect(self):
		return QRectF(self._x, self._y, self._diameter + 2, self._diameter + 2)
		
class PFSRelation(PFSElement):
	def __init__(self, id, source, target):
		super(PFSElement, self).__init__(id)
		self._source = source
		self._target = target
		
	def __del__(self):
		self._source.remInRelation(self)
		self._target.remOutRelation(self)
		
	def createRelation(id, source, target):
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
		