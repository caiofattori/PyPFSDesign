from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QToolBar, QWidgetAction, QMainWindow
from toolbutton import PFSToolButton

class PFSWindow(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		mainLayout = QVBoxLayout()
		
		self.setLayout(mainLayout)
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		toolBar = QToolBar()
		
		toolBar = self.addToolBar("teste")
		ac = toolBar.addWidget(PFSActivityButton())
		ac.setVisible(True)
		wind = PFSWindow()
		self.setCentralWidget(wind)

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	win = PFSMain()
	win.show()
	sys.exit(app.exec_())