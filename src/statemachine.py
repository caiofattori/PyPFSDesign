from PyQt5.QtCore import QStateMachine, QState, QEvent
from PyQt5.QtWidgets import QStatusBar

class PFSStateNormal(QState):
    def __init__(self):
        super(QState, self).__init__()
        
class PFSStateInsActivity(QState):
    def __init__(self, statusBar: QStatusBar):
        super(QState, self).__init__()
        self._statusBar = statusBar
        
    def onEntry(self, ev: QEvent):
        self._statusBar.showMessage("Clique na tela para adicionar uma Atividade")
        self.machine()._sActivity = True
        
    def onExit(self, ev: QEvent):
        self._statusBar.showMessage("")
        self.machine()._sActivity = False    

class PFSStateInsDistributor(QState):
    def __init__(self, statusBar: QStatusBar):
        super(QState, self).__init__()
        self._statusBar = statusBar
    
    def onEntry(self, ev: QEvent):
        self._statusBar.showMessage("Clique na tela para adicionar um Distribuidor")
        self.machine()._sDistributor = True
        
    def onExit(self, ev: QEvent):
        self._statusBar.showMessage("")
        self.machine()._sDistributor = False

class PFSStateInsRelationSource(QState):
    def __init__(self, statusBar: QStatusBar):
        super(QState, self).__init__()
        self._statusBar = statusBar
    
    def onEntry(self, ev: QEvent):
        self._statusBar.showMessage("Selecione o nó de origem")
        self.machine()._sRelationS = True
        
    def onExit(self, ev: QEvent):
        self._statusBar.showMessage("")
        self.machine()._sRelationS = False

class PFSStateInsRelationTarget(QState):
    def __init__(self, statusBar: QStatusBar):
        super(QState, self).__init__()
        self._statusBar = statusBar
    
    def onEntry(self, ev: QEvent):
        self._statusBar.showMessage("Selecione o nó de destino")
        self.machine()._sRelationT = True
        
    def onExit(self, ev: QEvent):
        self._statusBar.showMessage("")
        self.machine()._sRelationT = False

class PFSStateMachine(QStateMachine):
    def __init__(self, window):
        super(QStateMachine, self).__init__()
        self._sDistributor = False
        self._sActivity = False
        self._sRelationS = False
        self._sRelationT = False
        normal = PFSStateNormal()
        insActivity = PFSStateInsActivity(window.statusBar())
        insDistributor = PFSStateInsDistributor(window.statusBar())
        insRelationS = PFSStateInsRelationSource(window.statusBar())
        insRelationT = PFSStateInsRelationTarget(window.statusBar())
        normal.addTransition(window.btnActivity.clicked, insActivity)
        normal.addTransition(window.btnDistributor.clicked, insDistributor)
        normal.addTransition(window.btnRelation.clicked, insRelationS)
        insDistributor.addTransition(window.btnActivity.clicked, insActivity)
        insActivity.addTransition(window.btnDistributor.clicked, insDistributor)
        insDistributor.addTransition(window.btnRelation.clicked, insRelationS)
        insRelationS.addTransition(window.btnDistributor.clicked, insDistributor)
        insRelationT.addTransition(window.btnDistributor.clicked, insDistributor)
        insActivity.addTransition(window.btnRelation.clicked, insRelationS)
        insRelationS.addTransition(window.btnActivity.clicked, insActivity)
        insRelationT.addTransition(window.btnActivity.clicked, insActivity)
        self.insActivity = insActivity
        self.normal = normal
        self.insDistributor = insDistributor
        self.insRelationS = insRelationS
        self.insRelationT = insRelationT
        self.trans1 = None
        self.trans2 = None
        self.trans3 = None
        self.trans4 = None
        self.addState(normal)
        self.addState(insActivity)
        self.addState(insDistributor)
        self.addState(insRelationS)
        self.addState(insRelationT)
        self.setInitialState(normal)
        
    def fixTransitions(self, scene):
        if self.trans1 is not None:
            self.insActivity.removeTransition(self.trans1)
            self.insDistributor.removeTransition(self.trans2)
            self.insRelationS.removeTransition(self.trans3)
            self.insRelationS.removeTransition(self.trans4)
        self.trans1 = self.insActivity.addTransition(scene.inserted, self.normal)
        self.trans2 = self.insDistributor.addTransition(scene.inserted, self.normal)		        
        self.trans3 = self.insRelationS.addTransition(scene.inserted, self.insRelationT)
        self.trans4 = self.insRelationT.addTransition(scene.inserted, self.normal)