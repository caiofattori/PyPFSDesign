from PyQt5.QtWidgets import QGraphicsItem

class PFSElement(QGraphicsItem):
	def __init__(self, id):
		super(QGraphicsItem, self).__init__()
		self._id = id
		
class PFSNode(PFSElement):
	def __init__(self, id, x, y):
		super(PFSElement, self).__init__(id)
		self._inRelations = []
		self._outRelations = []
		self._x = x
		self._y = y
		
	def addInRelation(self, relat):
		if relat not in self._inRelations:
			self._inRelations.append(relat)
			return True
		return False
		
	def addOutRelation(self, relat):
		if relat not in self._outRelations:
			self._outRelations.append(relat)
			return True
		return False
		
	def remInRelation(self, relat):
		if relat in self._inRelations:
			self._inRelations.remove(relat)
			return True
		return False
		
	def remOutRelation(self, relat):
		if relat in self._outRelations:
			self._outRelations.remove(relat)
			return True
		return False