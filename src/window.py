from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton
from page import PFSPage
from PyQt5.QtGui import QIcon, QKeySequence

class PFSWindow(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		mainLayout = QHBoxLayout()
		self.setLayout(mainLayout)
		self._tab = QTabWidget()
		mainLayout.addWidget(self._tab)
		
	def newPage(self):
		w = PFSPage.newPage()
		self._tab.addTab(w, w.getTabName())
	
	def actionDistributor(self):
		self._tab.currentWidget().stateDistributor()
	
	def actionActivity(self):
		self._tab.currentWidget().stateActivity()		
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		wind = PFSWindow()
		icoNew = QIcon.fromTheme("document-new", QIcon())
		actNew = QAction(icoNew, "New Model", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		actNew.triggered.connect(wind.newPage)
		toolBar = self.addToolBar("Basic")
		toolBar.addAction(actNew)
		toolBar = self.addToolBar("Elements")
		btn = PFSActivityButton()
		btn.clicked.connect(wind.actionActivity)
		ac = toolBar.addWidget(btn)
		ac.setVisible(True)
		btn = PFSDistributorButton()
		btn.clicked.connect(wind.actionDistributor)
		ac = toolBar.addWidget(btn)
		ac.setVisible(True)
		ac = toolBar.addWidget(PFSRelationButton())
		ac.setVisible(True)		
		
		self.setCentralWidget(wind)

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	win = PFSMain()
	win.show()
	sys.exit(app.exec_())