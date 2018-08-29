from PyQt5.QtWidgets import QUndoStack, QUndoCommand

class PFSUndoDeleteRelation(QUndoCommand):
    def __init__(self, item):
        super(QUndoCommand, self).__init__()
        self._stored = item
        self._stored.scene().removeItem(self)

class PFSUndoDeleteNode(QUndoCommand):
    def __init__(self, item):
        super(QUndoCommand, self).__init__()
        self._stored = item
        self._stored.scene().removeItem(self)
        
        