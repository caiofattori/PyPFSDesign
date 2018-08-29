from PyQt5.QtWidgets import QUndoStack, QUndoCommand

class PFSUndoDeleteRelation(QUndoCommand):
    def __init__(self, item):
        super(QUndoCommand, self).__init__()
        self._stored = item
        self._stored.scene().removeItem(self)
        self._stored._source._outRelations.remove(self._stored)
        self._stored._target._inRelations.remove(self._stored)

class PFSUndoDeleteNode(QUndoCommand):
    def __init__(self, item):
        super(QUndoCommand, self).__init__()
        self._stored = item
        self._stored.scene().removeItem(self)
        self._copyInRelations = self._stored._inRelations.copy()
        self._copyOutRelations = self._stored._outRelations.copy()
        
        