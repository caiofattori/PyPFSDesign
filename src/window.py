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
		w = PFSPage()
		self._tab.addTab(w, w.getTabName())
		
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
		ac = toolBar.addWidget(PFSActivityButton())
		ac.setVisible(True)
		ac = toolBar.addWidget(PFSDistributorButton())
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