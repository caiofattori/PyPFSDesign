from PyQt5.QtCore import QStateMachine, QState, QEvent, Qt
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtGui import QCursor

class PFSStateNormal(QState):
	def __init__(self):
		super(QState, self).__init__()
		
	def onEntry(self, ev: QEvent):
		self.machine()._sNormal = True
		
	def onExit(self, ev: QEvent):
		self.machine()._sNormal = False

class PFSStatePasting(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.actPaste
		
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Clique na tela para posicionar a colar")
		self.machine()._sPasting = True
		self._button.setChecked(True)
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self.machine()._sPasting = False
		self._button.setChecked(False)

class PFSStateEditPoint(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnEditPoint
		self._tab = window.wind._tab
		
	def onEntry(self, ev: QEvent):
		self._tab.currentWidget()._tab.setCursor(QCursor(Qt.CrossCursor))
		self._tab.currentWidget()._tab.currentWidget()._scene.update()
		self._statusBar.showMessage("No ponto que deseja mover")
		self.machine()._sEditPoint = True
		self._button.setChecked(True)
		
	def onExit(self, ev: QEvent):
		self._tab.currentWidget()._tab.setCursor(QCursor(Qt.ArrowCursor))
		self._tab.currentWidget()._tab.currentWidget()._scene.update()
		self._statusBar.showMessage("")
		self.machine()._sEditPoint = False
		self._button.setChecked(False)
		
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

class PFSStateInsSecondaryFlowSource(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnSecFlow
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Selecione o nó de origem")
		self._button.setChecked(True)
		self.machine()._sSFlowS = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sSFlowS = False

class PFSStateInsSecondaryFlowTarget(QState):
	def __init__(self, window):
		super(QState, self).__init__()
		self._statusBar = window.statusBar()
		self._button = window.btnSecFlow
	
	def onEntry(self, ev: QEvent):
		self._statusBar.showMessage("Selecione o nó de destino")
		self._button.setChecked(True)
		self.machine()._sSFlowT = True
		
	def onExit(self, ev: QEvent):
		self._statusBar.showMessage("")
		self._button.setChecked(False)
		self.machine()._sSFlowT = False

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
		self._sPasting = False
		self._sSFlowS = False
		self._sSFlowT = False
		self._sEditPoint = False
		normal = PFSStateNormal()
		insActivity = PFSStateInsActivity(window)
		insDistributor = PFSStateInsDistributor(window)
		insRelationS = PFSStateInsRelationSource(window)
		insRelationT = PFSStateInsRelationTarget(window)
		tiping = PFSStateTiping(window)
		pasting = PFSStatePasting(window)
		point = PFSStateEditPoint(window)
		insSecFlowS = PFSStateInsSecondaryFlowSource(window)
		insSecFlowT = PFSStateInsSecondaryFlowTarget(window)
		normal.addTransition(window.btnActivity.clicked, insActivity)
		normal.addTransition(window.btnDistributor.clicked, insDistributor)
		normal.addTransition(window.btnRelation.clicked, insRelationS)
		normal.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		insDistributor.addTransition(window.btnActivity.clicked, insActivity)
		insDistributor.addTransition(window.btnDistributor.clicked, normal)
		insActivity.addTransition(window.btnDistributor.clicked, insDistributor)
		insActivity.addTransition(window.btnActivity.clicked, normal)
		insDistributor.addTransition(window.btnRelation.clicked, insRelationS)
		insDistributor.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		insRelationS.addTransition(window.btnDistributor.clicked, insDistributor)
		insSecFlowS.addTransition(window.btnDistributor.clicked, insDistributor)
		insRelationS.addTransition(window.btnRelation.clicked, normal)
		insSecFlowS.addTransition(window.btnRelation.clicked, normal)
		insRelationT.addTransition(window.btnDistributor.clicked, insDistributor)
		insSecFlowT.addTransition(window.btnDistributor.clicked, insDistributor)
		insRelationT.addTransition(window.btnRelation.clicked, normal)
		insSecFlowT.addTransition(window.btnSecFlow.clicked, normal)
		insActivity.addTransition(window.btnRelation.clicked, insRelationS)
		insActivity.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		insRelationS.addTransition(window.btnActivity.clicked, insActivity)
		insSecFlowS.addTransition(window.btnActivity.clicked, insActivity)
		insRelationT.addTransition(window.btnActivity.clicked, insActivity)
		insSecFlowT.addTransition(window.btnActivity.clicked, insActivity)
		insDistributor.addTransition(window.tabChanged, normal)
		insActivity.addTransition(window.tabChanged, normal)
		insRelationS.addTransition(window.tabChanged, normal)
		insSecFlowS.addTransition(window.tabChanged, normal)
		insRelationT.addTransition(window.tabChanged, normal)
		insSecFlowT.addTransition(window.tabChanged, normal)
		tiping.addTransition(window.tabChanged, normal)
		normal.addTransition(window.paste, pasting)
		insActivity.addTransition(window.paste, pasting)
		insDistributor.addTransition(window.paste, pasting)
		insRelationS.addTransition(window.paste, pasting)
		insSecFlowS.addTransition(window.paste, pasting)
		insRelationT.addTransition(window.paste, pasting)
		insSecFlowT.addTransition(window.paste, pasting)
		insRelationS.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		insSecFlowS.addTransition(window.btnRelation.clicked, insRelationS)
		insRelationT.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		insSecFlowT.addTransition(window.btnRelation.clicked, insRelationS)
		#create transitions of edit point state for future reference
		point.addTransition(window.btnEditPoint.clicked, normal)
		point.addTransition(window.btnActivity.clicked, insActivity)
		point.addTransition(window.btnDistributor.clicked, insDistributor)
		point.addTransition(window.btnRelation.clicked, insRelationS)
		point.addTransition(window.btnSecFlow.clicked, insSecFlowS)
		point.addTransition(window.paste, pasting)
		point.addTransition(window.tabChanged, normal)
		normal.addTransition(window.btnEditPoint.clicked, point)
		insDistributor.addTransition(window.btnEditPoint.clicked, point)
		insActivity.addTransition(window.btnEditPoint.clicked, point)
		insRelationS.addTransition(window.btnEditPoint.clicked, point)
		insRelationT.addTransition(window.btnEditPoint.clicked, point)
		insSecFlowS.addTransition(window.btnEditPoint.clicked, point)
		insSecFlowT.addTransition(window.btnEditPoint.clicked, point)
		
		self.editPoint = point
		self.insActivity = insActivity
		self.normal = normal
		self.insDistributor = insDistributor
		self.insRelationS = insRelationS
		self.insSecFlowS = insSecFlowS
		self.insRelationT = insRelationT
		self.insSecFlowT = insSecFlowT
		self.tiping = tiping
		self.pasting = pasting
		self.addState(normal)
		self.addState(insActivity)
		self.addState(insDistributor)
		self.addState(insRelationS)
		self.addState(insSecFlowS)
		self.addState(insRelationT)
		self.addState(insSecFlowT)
		self.addState(tiping)
		self.addState(pasting)
		self.addState(point)
		self.setInitialState(normal)
		
	def fixTransitions(self, scene):
		self.trans1 = self.insActivity.addTransition(scene.inserted, self.normal)
		self.trans2 = self.insDistributor.addTransition(scene.inserted, self.normal)				
		self.trans3 = self.insRelationS.addTransition(scene.inserted, self.insRelationT)
		self.trans4 = self.insRelationT.addTransition(scene.inserted, self.normal)
		self.trans5 = self.tiping.addTransition(scene.inserted, self.normal)
		self.trans6 = self.normal.addTransition(scene.edited, self.tiping)
		self.trans7 = self.insRelationT.addTransition(scene.shiftInserted, self.insRelationS)
		self.trans8 = self.pasting.addTransition(scene.inserted, self.normal)
		self.trans9 = self.insSecFlowS.addTransition(scene.inserted, self.insSecFlowT)
		self.trans10 = self.insSecFlowT.addTransition(scene.inserted, self.normal)
		self.trans11 = self.insSecFlowT.addTransition(scene.shiftInserted, self.insSecFlowS)