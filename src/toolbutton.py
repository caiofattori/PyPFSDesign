from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPainter, QFont, QPaintEvent, QTextOption, QBrush, QPen
from PyQt5.QtCore import Qt
	
class PFSActivityButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
		self.setCheckable(True)
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		if self.isChecked():
			p.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
			p.drawRect(self.rect())
		p.setPen(Qt.black)
		p.setFont(QFont("Helvetica", 12))
		p.drawText(self.rect(), Qt.AlignCenter, "[Ac]")
		
class PFSDistributorButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
		self.setCheckable(True)
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		if self.isChecked():
			p.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
			p.drawRect(self.rect())		
		p.setPen(Qt.black)
		r = self.rect()
		p.drawEllipse(r.left()+5, r.top()+5, r.width()-10, r.height()-10)
		
class PFSRelationButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
		self.setCheckable(True)
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		if self.isChecked():
			p.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
			p.drawRect(self.rect())		
		p.setPen(Qt.black)
		r = self.rect()
		p.drawLine(r.left() + 5, r.bottom() - 5, r.right() - 5, r.top() + 5)
		p.drawLine(r.right() - 15, r.top() + 10, r.right() - 5, r.top() + 5)
		p.drawLine(r.right() - 10, r.top() + 15, r.right() - 5, r.top() + 5)
		
class PFSSecondaryFlowButton(QToolButton):
	def __init__(self):
		QToolButton.__init__(self)
		self.setCheckable(True)
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		if self.isChecked():
			p.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
			p.drawRect(self.rect())		
		p.setPen(QPen(QBrush(Qt.black, Qt.SolidPattern), 5))
		#p.pen().setWidth(5)
		r = self.rect()
		p.drawLine(r.left() + 5, r.bottom() - 5, r.left() + 5, r.center().y())
		p.drawLine(r.left() + 5, r.center().y() , r.right() - 10, r.center().y())
		p.drawLine(r.right() - 10, r.center().y() , r.right() - 10, r.top() + 5)
		p.drawLine(r.right() - 15, r.top() + 10, r.right() - 10, r.top() + 5)
		p.drawLine(r.right() - 5, r.top() + 10, r.right() - 10, r.top() + 5)
		
class PFSAddButton(QToolButton):
	def __init__(self):
		QToolButton.__init__(self)
	
	def paintEvent(self, ev: QPaintEvent):
		p = QPainter(self)
		r = self.rect()
		p.drawEllipse(r.x(), r.y(), r.width()-1, r.height()-1)
		p.drawText(r, Qt.AlignCenter, "+")