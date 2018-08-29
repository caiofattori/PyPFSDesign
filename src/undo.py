from PyQt5.QtWidgets import QUndoStack, QUndoCommand

class PFSUndoDelete(QUndoCommand):
    def __init__(self, itema):
        super(QUndoCommand, self).__init__()
        self._stored = items
        self._scene = items[0].scene()
        for item in self._stored:
        	self._scene.removeItem(item)
        self._scene.update()
        	
     def undo(self):
         for item in self._stored:
             self._scene.addItem(item)
         self._scene.update()
         
     def redo(self):
         for item in self._stored:
             self._scene.removeItem(item)
         self._scene.update()
        