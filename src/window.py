from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton
from page import PFSPage
from PyQt5.QtGui import QIcon, QKeySequence
from statemachine import PFSStateMachine

class PFSWindow(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		mainLayout = QHBoxLayout()
		self.setLayout(mainLayout)
		self._tab = QTabWidget()
		mainLayout.addWidget(self._tab)
		self._sm = None
	
	def setStateMachine(self, sm):
		self._sm = sm
		
	def newPage(self):
		w = PFSPage.newPage(self._sm)
		self._tab.addTab(w, w.getTabName())
		self._sm.fixTransitions(w._scene)		
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.wind = PFSWindow()
		icoNew = QIcon.fromTheme("document-new", QIcon())
		actNew = QAction(icoNew, "New Model", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		actNew.triggered.connect(self.wind.newPage)
		toolBar = self.addToolBar("Basic")
		toolBar.addAction(actNew)
		toolBar = self.addToolBar("Elements")
		self.btnActivity = PFSActivityButton()
		ac = toolBar.addWidget(self.btnActivity)
		ac.setVisible(True)
		self.btnDistributor = PFSDistributorButton()
		ac = toolBar.addWidget(self.btnDistributor)
		ac.setVisible(True)
		ac = toolBar.addWidget(PFSRelationButton())
		ac.setVisible(True)		
		self.setCentralWidget(self.wind)
		
	def setStateMachine(self, sm):
		self.wind.setStateMachine(sm)

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	win = PFSMain()
	stateMachine = PFSStateMachine(win)
	win.setStateMachine(stateMachine)
	stateMachine.start()
	win.show()
	sys.exit(app.exec_())