from PyQt5.QtCore import QStateMachine, QState, QEvent
from window import PFSMain
from page import PFSScene

class PFSStateNormal(QState):
    def __init__(self):
        super(QState, self).__init__()
        
class PFSStateInsActivity(QState):
    def __init__(self):
        super(QState, self).__init__()
        
    def onEntry(self, ev: QEvent):
        self.machine()._sActivity = True
        
    def onExit(self, ev: QEvent):
        self.machine()._sActivity = False    

class PFSStateInsDistributor(QState):
    def __init__(self):
        super(QState, self).__init__()    
    
    def onEntry(self, ev: QEvent):
        self.machine()._sDistributor = True
        
    def onExit(self, ev: QEvent):
        self.machine()._sDistributor = False

class PFSStateMachine(QStateMachine):
    def __init__(self, window: PFSMain):
        super(QStateMachine, self).__init__()
        self._sDistributor = False
        self._sActivity = False
        normal = PFSStateNormal()
        insActivity = PFSStateInsActivity()
        insDistributor = PFSStateInsDistributor()
        normal.addTransition(window.btnActivity.clicked, insActivity)
        normal.addTransition(window.btnDistributor.clicked, insDistributor)
        insDistributor.addTransition(window.btnActivity.clicked, insActivity)
        insActivity.addTransition(window.btnDistributor.clicked, insDistributor)
        self.insActivity = insActivity
        self.normal = normal
        self.insDistributor = insDistributor
        self.trans1 = None
        self.trans2 = None
        self.addState(normal)
        self.addState(insActivity)
        self.addState(insDistributor)
        self.setInitialState(normal)
        
    def fixTransitions(self, scene: PFSScene):
        if self.trans1 is not None:
            self.insActivity.removeTransition(self.trans1)
            self.insDistributor.removeTransition(self.trans2)
        self.trans1 = self.insActivity.addTransition(scene.inserted, self.normal)
        self.trans2 = self.insDistributor.addTransition(scene.inserted, self.normal)		        