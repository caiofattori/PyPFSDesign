from PyQt5.QtCore import QStateMachine, QState, QEvent
from PyQt5.QtWidgets import QStatusBar

class PFSStateNormal(QState):
	def __init__(self):
		super(QState, self).__init__()
		
	def onEntry(self, ev: QEvent):
		self.machine()._sNormal = True
		
	def onExit(self, ev: QEvent):
		self.machine()._sNormal = False
		
class PFSStateInsActivity(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnActivity
		
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Clique na tela para adicionar uma Atividade")
		self._button.setChecked(True)
		self.machine()._sActivity = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sActivity = False

class PFSStateInsDistributor(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnDistributor
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Clique na tela para adicionar um Distribuidor")
		self._button.setChecked(True)
		self.machine()._sDistributor = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sDistributor = False

class PFSStateInsRelationSource(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnRelation
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Selecione o nó de origem")
		self._button.setChecked(True)
		self.machine()._sRelationS = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sRelationS = False

class PFSStateInsRelationTarget(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnRelation
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Selecione o nó de destino")
		self._button.setChecked(True)
		self.machine()._sRelationT = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sRelationT = False
		
class PFSStateTiping(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Editando atividade")
		self.machine()._sTiping = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self.machine()._sTiping = False

class PFSStateMachine(QStateMachine):
	def __init__(self, window):
		super(QStateMachine, self).__init__()
		self._sNormal = False
		self._sDistributor = False
		self._sActivity = False
		self._sRelationS = False
		self._sRelationT = False
		self._sTiping = False
		normal = PFSStateNormal()
		insActivity = PFSStateInsActivity(window)
		insDistributor = PFSStateInsDistributor(window)
		insRelationS = PFSStateInsRelationSource(window)
		insRelationT = PFSStateInsRelationTarget(window)
		tiping = PFSStateTiping(window)
		normal.addTransition(window.btnActivity.clicked, insActivity)
		normal.addTransition(window.btnDistributor.clicked, insDistributor)
		normal.addTransition(window.btnRelation.clicked, insRelationS)
		insDistributor.addTransition(window.btnActivity.clicked, insActivity)
		insDistributor.addTransition(window.btnDistributor.clicked, normal)
		insActivity.addTransition(window.btnDistributor.clicked, insDistributor)
		insActivity.addTransition(window.btnActivity.clicked, normal)
		insDistributor.addTransition(window.btnRelation.clicked, insRelationS)
		insRelationS.addTransition(window.btnDistributor.clicked, insDistributor)
		insRelationS.addTransition(window.btnRelation.clicked, normal)
		insRelationT.addTransition(window.btnDistributor.clicked, insDistributor)
		insRelationT.addTransition(window.btnRelation.clicked, normal)
		insActivity.addTransition(window.btnRelation.clicked, insRelationS)
		insRelationS.addTransition(window.btnActivity.clicked, insActivity)
		insRelationT.addTransition(window.btnActivity.clicked, insActivity)
		self.insActivity = insActivity
		self.normal = normal
		self.insDistributor = insDistributor
		self.insRelationS = insRelationS
		self.insRelationT = insRelationT
		self.tiping = tiping
		self.trans1 = None
		self.trans2 = None
		self.trans3 = None
		self.trans4 = None
		self.trans5 = None
		self.trans6 = None
		self.addState(normal)
		self.addState(insActivity)
		self.addState(insDistributor)
		self.addState(insRelationS)
		self.addState(insRelationT)
		self.addState(tiping)
		self.setInitialState(normal)
		
	def fixTransitions(self, scene):
		'''if self.trans1 is not None:
			self.insActivity.removeTransition(self.trans1)
			self.insDistributor.removeTransition(self.trans2)
			self.insRelationS.removeTransition(self.trans3)
			self.insRelationT.removeTransition(self.trans4)
			self.tiping.removeTransition(self.trans5)
			self.normal.removeTransition(self.trans6)'''
		self.trans1 = self.insActivity.addTransition(scene.inserted, self.normal)
		self.trans2 = self.insDistributor.addTransition(scene.inserted, self.normal)				
		self.trans3 = self.insRelationS.addTransition(scene.inserted, self.insRelationT)
		self.trans4 = self.insRelationT.addTransition(scene.inserted, self.normal)
		self.trans5 = self.tiping.addTransition(scene.inserted, self.normal)
		self.trans6 = self.normal.addTransition(scene.edited, self.tiping)
		self.trans7 = self.insRelationT.addTransition(scene.shiftInserted, self.insRelationS)