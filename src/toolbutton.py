from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPainter, QFont, QPaintEvent, QTextOption, QBrush
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