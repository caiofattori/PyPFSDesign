from generic import *

class PFSActivity(PFSNode):
	
	def __init__(self, id, x, y, text="Atividade"):
		super(PFSNode, self).__init__(id, x, y)
		self._text = text
		self._subNet = None
		self._tooltip = ""
		
	def setText(self, text):
		self._text = text
		
	def setTooltip(self, text):
		self._tooltip = text
		
class PFSDistributor(PFSNode):
	
	def __init__(self, id, x, y):
		super(PFSNode, self).__init__(id, x, y)
		self._tooltip = ""
		
	def setTooltip(self, text):
		self._tooltip = text
		
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
		