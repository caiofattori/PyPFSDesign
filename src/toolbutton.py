from PyQt5.QtWidgets import QToolButton, QTextEdit, QGraphicsProxyWidget
from PyQt5.QtGui import QPainter, QFont, QPaintEvent, QTextOption
from PyQt5.QtCore import Qt

class PFSTextBox(QGraphicsProxyWidget):
	def __init__(self, scene, activity):
		super(QGraphicsProxyWidget, self).__init__()
		self._activity = activity
		self._item = QTextEdit()
		txt = activity._text.splitlines()
		self._item.setAlignment(Qt.AlignCenter)
		for i in range(len(txt)):
			if i != 0:
				self._item.insertPlainText("\n")
			self._item.insertPlainText(txt[i])
			self._item.setAlignment(Qt.AlignCenter)
		self.setWidget(self._item)
		self._scene = scene
		self._item.selectAll()
		self._item.setLineWrapMode(QTextEdit.NoWrap)
		self._shift = False
		
	def keyPressEvent(self, ev):
		if ev.key() == Qt.Key_Shift:
			self._shift = True
		if (ev.key() == Qt.Key_Enter or ev.key() == Qt.Key_Return) and self._shift:
			self._activity.setText(self._item.toPlainText())
			self._scene.inserted.emit()
			self._scene.removeItem(self)
			return
		QGraphicsProxyWidget.keyPressEvent(self, ev)
		r = self._item.fontMetrics().size(Qt.TextExpandTabs, self._item.toPlainText())
		self._item.setMinimumSize(r.width() + 20, r.height() + 20)
		self._item.resize(r.width()+20, r.height()+20)
	
	def keyReleaseEvent(self, ev):
		if ev.key() == Qt.Key_Shift:
			self._shift = False
		QGraphicsProxyWidget.keyReleaseEvent(self, ev)
		
		
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