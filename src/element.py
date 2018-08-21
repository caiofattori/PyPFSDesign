from generic import *
from xml import PFSXmlBase
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QFontMetrics, QPen, QBrush

class PFSActivity(PFSNode):
	
	def __init__(self, id, x, y, text="Atividade"):
		PFSNode.__init__(self, id, x, y)
		self._subNet = None
		self._tooltip = ""
		self._textFont = QFont("Helvetica", 15)
		self._lineNumbers = 1
		self._charsNumbers = 0
		self.setText(text)
		self._fontMetrics = QFontMetrics(self._textFont)
		
	def generateXml(self, xml):
		PFSXmlBase.open(xml)
		xml.writeStartElement("activity")
		xml.writeAttribute("id", selt._id)
		PFSXmlBase.text(xml, self._text, 0, 0, font=self._textFont, tag="text")
		xml.writeEndElement() #fecha activity
		PFSXmlBase.close(xml)
		
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
		if self.STANDARD_PEN.color().
		
	def setTooltip(self, text):
		self._tooltip = text
		
	
	def generateXml(self, xml):
		PFSXmlBase.open(xml)
		xml.writeStartElement("distributor")
		xml.writeAttribute("id", selt._id)
		xml.writeStartElement("graphics")
		PFSXmlBase.rect(xml, self.mapRectFromScene(), self._pen)
		xml.writeEndElement() #fecha graphics
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)
	
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
		