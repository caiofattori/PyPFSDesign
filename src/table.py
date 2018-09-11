from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QComboBox, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class PFSTableLabel(QTableWidgetItem):
	def __init__(self, text):
		QTableWidgetItem.__init__(self, text)
		self.setFlags(Qt.NoItemFlags)
		
	def comparePrevious(self):
		return False

class PFSTableNormal(QTableWidgetItem):
	def __init__(self, text):
		QTableWidgetItem.__init__(self, text)
		self.setFlags(Qt.NoItemFlags)
		
	def comparePrevious(self):
		return False

class PFSTableObject(QObject):
	edited = pyqtSignal(object)
	def __init__(self):
		super(QObject, self).__init__()

class PFSTableValueText(QTableWidgetItem):
	def __init__(self, text):
		QTableWidgetItem.__init__(self, text)
		self._obj = PFSTableObject()
		self.edited = self._obj.edited
		self._text = text
	
	def comparePrevious(self):
		return self._text != self.text()
	
	def value(self):
		return self._text
	
class PFSTableValueButton(QPushButton):
	def __init__(self, text):
		QPushButton.__init__(self, text)
		self._obj = PFSTableObject()
		self.edited = self._obj.edited
	
	def comparePrevious(self):
		return False
	
class PFSTableValueCombo(QComboBox):
	def __init__(self, opts: dict, std):
		QComboBox.__init__(self)
		self._list = opts
		for key, op in opts.items():
			self.addItem(key)
			if op == std:
				self.setCurrentText(key)
		self._obj = PFSTableObject()
		self.edited = self._obj.edited
	
	def comparePrevious(self):
		return False
	
	def updateText(self, value):
		for key, op in self._list.items():
			if op == value:
				self.blockSignals(True)
				self.setCurrentText(key)
				self.blockSignals(False)
				return

class PFSTableValueCheck(QCheckBox):
	def __init__(self, txt, value):
		QCheckBox.__init__(self, txt)
		self.setChecked(value)
		
	def comparePrevious(self):
		return False
		
class PFSTableValueBox(QWidget):
	def __init__(self, txt, value):
		QCheckBox.__init__(self, txt)
		self.setChecked(value)
		
	def comparePrevious(self):
		return False