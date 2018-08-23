from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction, QFileDialog
from PyQt5.QtCore import QFile, QIODevice, QXmlStreamWriter, QFileInfo, QDir
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton
from page import PFSNet
from PyQt5.QtGui import QIcon, QKeySequence
from statemachine import PFSStateMachine
from xml import PFSXmlBase

class PFSWindow(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		mainLayout = QHBoxLayout()
		self.setLayout(mainLayout)
		self._tab = QTabWidget()
		mainLayout.addWidget(self._tab)
		self._sm = None
		self._idNet = 0
		self._lastPath = "./"
		self._tab.currentChanged.connect(self.changeTab)
	
	def changeTab(self, index):
		net = self._tab.widget(index)
		if net._filepath is not None:
			self._lastPath = net._filepath
	
	def setStateMachine(self, sm):
		self._sm = sm
		
	def newNet(self):
		w = PFSNet.newNet("n" + str(self._idNet), self._sm)
		w.changed.connect(self.changeCurrentTabName)
		self._idNet = self._idNet + 1
		i = self._tab.addTab(w, w.getTabName())
		self._tab.setCurrentIndex(i)
		self._sm.fixTransitions(w._pages[0]._scene)
	
	def saveNet(self):
		net = self._tab.currentWidget()
		if net._filename is None:
			filename, filter = QFileDialog.getSaveFileName(self, "Salvar arquivo...", self._lastPath, "XML files (*.xml *.pnml)")
			if filename is None or filename == "":
				return
			if not (filename.endswith(".xml") or filename.endswith(".pnml")):
				filename = filename + ".xml"
			file = QFile(filename)
			file.open(QIODevice.WriteOnly)
			xml = QXmlStreamWriter(file)
			net.generateXml(xml)
			f = QFileInfo(filename)
			net._filename = f.fileName()
			net._filepath = f.absolutePath()
			file.close()
		else:
			file = QFile(QFileInfo(QDir(net._filepath), net._filename).absoluteFilePath())
			file.open(QIODevice.WriteOnly)
			xml = QXmlStreamWriter(file)
			net.generateXml(xml)
			file.close()
		net.setSaved(True)
		self._lastPath = net._filepath
		
	def changeCurrentTabName(self):
		self._tab.setTabText(self._tab.currentIndex(), self._tab.currentWidget().getTabName())
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.wind = PFSWindow()
		icoNew = QIcon.fromTheme("document-new", QIcon())
		actNew = QAction(icoNew, "New Model", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		actNew.triggered.connect(self.wind.newNet)
		icoSave = QIcon.fromTheme("document-save", QIcon())
		actSave = QAction(icoSave, "Save Model", self)
		actSave.setShortcuts(QKeySequence.Save)
		actSave.setStatusTip("Salva o modelo em um arquivo")
		actSave.triggered.connect(self.wind.saveNet)		
		toolBar = self.addToolBar("Basic")
		toolBar.addAction(actNew)
		toolBar.addAction(actSave)
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