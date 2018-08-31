from PyQt5.QtWidgets import QUndoStack, QUndoCommand

class PFSUndoDelete(QUndoCommand):
	def __init__(self, items):
		super(QUndoCommand, self).__init__()
		self._stored = items
		self._scene = items[0].scene()
		for item in self._stored:
			self._scene.removeItem(item)
		self._scene.clearSelection()
		self._scene.update()
			
	def undo(self):
		for item in self._stored:
			self._scene.addItem(item)
		self._scene.clearSelection()
		self._scene.update()
		 
	def redo(self):
		for item in self._stored:
			self._scene.removeItem(item)
		self._scene.clearSelection()
		self._scene.update()
		
class PFSUndoAdd(QUndoCommand):
	def __init__(self, items, scene):
		super(QUndoCommand, self).__init__()
		self._stored = items
		self._scene = scene
		for item in self._stored:
			self._scene.addItem(item)
		self._scene.update()
			
	def undo(self):
		for item in self._stored:
			self._scene.removeItem(item)
		self._scene.update()
		 
	def redo(self):
		for item in self._stored:
			self._scene.addItem(item)
		self._scene.update()

class PFSUndoKeyMove(QUndoCommand):
	def __init__(self, items, dx, dy):
		super(QUndoCommand, self).__init__()
		self._stored = items
		self._scene = items[0].scene()
		self._dx = dx
		self._dy = dy
		self.first = True
		self._id = int(hash("K" + ",".join([x._id for x in self._stored])))
	
	def undo(self):
		for item in self._stored:
			item.move(-self._dx, -self._dy)
		self._scene.clearSelection()
		self._scene.update()

	def id(self):
		return self._id

	def mergeWith(self, other):
		if self.id() != other.id():
			return False
		self._dx = self._dx + other._dx
		self._dy = self._dy + other._dy
		return True
	
	def redo(self):
		for item in self._stored:
			item.move(self._dx, self._dy)
		if not self.first:
			self._scene.clearSelection()
		self.first = False
		self._scene.update()

class PFSUndoMouseMove(QUndoCommand):
	def __init__(self, items, dx, dy):
		super(QUndoCommand, self).__init__()
		self._stored = items
		self._scene = items[0].scene()
		self._dx = dx
		self._dy = dy
		self.first = True
		self._id = int(hash("M" + ",".join([x._id for x in self._stored])))
	
	def undo(self):
		for item in self._stored:
			item.move(-self._dx, -self._dy)
		self._scene.clearSelection()
		self._scene.update()

	def id(self):
		return self._id

	def mergeWith(self, other):
		if self.id() != other.id():
			return False
		self._dx = self._dx + other._dx
		self._dy = self._dy + other._dy
		return True
	
	def redo(self):
		for item in self._stored:
			item.move(self._dx, self._dy)
		if not self.first:
			self._scene.clearSelection()
		self.first = False
		self._scene.update()

class PFSUndoSetText(QUndoCommand):
	def __init__(self, item, text, scene=None):
		super(QUndoCommand, self).__init__()
		self._stored = item
		self._backText = item.getText()
		self._text = text
		self._scene = scene
			
	def undo(self):
		self._stored.setText(self._backText)
		if self._scene is not None:
			self._scene.update()
		 
	def redo(self):
		self._stored.setText(self._text)
		if self._scene is not None:
			self._scene.update()

class PFSUndoResizePage(QUndoCommand):
	def __init__(self, scene, fieldWidth, fieldHeight):
		super(QUndoCommand, self).__init__()
		self._width = fieldWidth
		self._height = fieldHeight
		self._newW = fieldWidth.text()
		self._newH = fieldHeight.text()
		self._oldW = str(scene.sceneRect().width())
		self._oldH = str(scene.sceneRect().height())
		self._scene = scene
			
	def undo(self):
		self._scene.resize(int(float(self._oldW)), int(float(self._oldH)))
		self._width.setText(self._oldW)
		self._height.setText(self._oldH)
		 
	def redo(self):
		self._scene.resize(int(float(self._newW)), int(float(self._newH)))
		self._width.setText(self._newW)
		self._height.setText(self._newH)

class PFSUndoRectPage(QUndoCommand):
	def __init__(self, scene, fieldWidth, fieldHeight, rect):
		super(QUndoCommand, self).__init__()
		self._nRect = rect
		self._oRect = scene.sceneRect()
		self._width = fieldWidth
		self._height = fieldHeight
		self._scene = scene
			
	def undo(self):
		self._scene.resize(self._oRect.width(), self._oRect.height(), -self._nRect.left(), -self._nRect.top())
		self._width.setText(str(self._oRect.width()))
		self._height.setText(str(self._oRect.height()))
		 
	def redo(self):
		self._scene.resize(self._nRect.width(), self._nRect.height(), self._nRect.left(), self._nRect.top())
		self._width.setText(str(self._nRect.width()))
		self._height.setText(str(self._nRect.height()))
		
class PFSUndoPropertyText(QUndoCommand):
	def __init__(self, prop):
		super(QUndoCommand, self).__init__()
		self._prop = prop
		self._old = prop._text
		self._new = prop.text()
			
	def undo(self):
		self._prop._obj.blockSignals(True)
		self._prop.setText(self._old)
		self._prop._obj.blockSignals(False)
		self._text = self._old
		 
	def redo(self):
		self._prop._obj.blockSignals(True)
		self._prop.setText(self._new)
		self._prop._obj.blockSignals(False)
		self._text = self._new