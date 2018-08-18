from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt

class PFSActivityButton(QToolButton):
	def __init__(self):
		super(QToolButton, self).__init__()
	
	def paintEvent(self, ev):
		p = QPainter(self)
		p.setPen(Qt.black)
		p.setFont(QFont("Helvetica", 12))
		p.drawText(self.rect(), Qt.AlignCenter, "[Ac]")