from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton

class PFSWindow(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		mainLayout = QHBoxLayout()
		self.setLayout(mainLayout)
		self._tab = QTabWidget()
		w = QWidget()
		self._tab.addTab(w, "Teste")
		mainLayout.addWidget(self._tab)
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		toolBar = QToolBar()
		toolBar = self.addToolBar("teste")
		ac = toolBar.addWidget(PFSActivityButton())
		ac.setVisible(True)
		ac = toolBar.addWidget(PFSDistributorButton())
		ac.setVisible(True)
		ac = toolBar.addWidget(PFSRelationButton())
		ac.setVisible(True)		
		wind = PFSWindow()
		self.setCentralWidget(wind)

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	win = PFSMain()
	win.show()
	sys.exit(app.exec_())