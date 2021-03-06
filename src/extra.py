from PyQt5.QtWidgets import QTextEdit, QGraphicsProxyWidget
from PyQt5.QtCore import Qt
from undo import *

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
			x = PFSUndoSetText(self._activity, self._item.toPlainText(), self.scene())
			x.setText("Mover")
			self.scene()._net.undoStack.push(x)
			self._activity.setSelected(False)
			self._scene.inserted.emit()
			self._scene.removeItem(self)
			return
		if ev.key() == Qt.Key_Escape:
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
