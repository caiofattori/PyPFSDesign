from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import QObject, pyqtSignal

class PFSAuxTree(QObject):
	clicked = pyqtSignal()
	def __init__(self):
		QObject.__init__(self)
		
class PFSTreeItem(QTreeWidgetItem):
	def __init__(self, parent, lst, type, ico=None):
		QTreeWidgetItem.__init__(self, parent, lst, type)
		if ico is not None:
			self.setIcon(0, ico)
		self._object = PFSAuxTree()
		self.clicked = self._object.clicked