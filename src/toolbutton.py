from PyQt5.QtWidgets import QToolButton, QGraphicsSimpleTextItem
from PyQt5.QtGui import QPainter, QFont, QPaintEvent
from PyQt5.QtCore import Qt

class PFSTextBox(QGraphicsSimpleTextItem):
	def __init__(self, scene, activity):
		super(QGraphicsSimpleTextItem, self).__init__(activity._text)
		self._activity = activity
		
	def boundingRect(self):
		return self._activity.boundingRect()
		
class PFSActivityButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		p.setPen(Qt.black)
		p.setFont(QFont("Helvetica", 12))
		p.drawText(self.rect(), Qt.AlignCenter, "[Ac]")
		
class PFSDistributorButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		p.setPen(Qt.black)
		r = self.rect()
		p.drawEllipse(r.left()+5, r.top()+5, r.width()-10, r.height()-10)
		
class PFSRelationButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		p.setPen(Qt.black)
		r = self.rect()
		p.drawLine(r.left() + 5, r.bottom() - 5, r.right() - 5, r.top() + 5)
		p.drawLine(r.right() - 15, r.top() + 10, r.right() - 5, r.top() + 5)
		p.drawLine(r.right() - 10, r.top() + 15, r.right() - 5, r.top() + 5)