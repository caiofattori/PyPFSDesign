from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction, QFileDialog
from PyQt5.QtCore import QFile, QIODevice, QXmlStreamWriter
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton
from page import PFSPage
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
	
	def setStateMachine(self, sm):
		self._sm = sm
		
	def newPage(self):
		w = PFSPage.newPage(self._sm)
		self._tab.addTab(w, w.getTabName())
		self._sm.fixTransitions(w._scene)
	
	def savePage(self):
		filename, filter = QFileDialog.getSaveFileName(self, "Salvar arquivo...", "./", "XML files (*.xml)")
		if filename is None:
			return
		file = QFile(filename)
		file.open(QIODevice.WriteOnly)
		xml = QXmlStreamWriter(file)
		xml.writeStartDocument()
		xml.writeStartElement("PetriNetDoc")
		xml.writeStartElement("net")
		xml.writeAttribute("id", "n1")
		PFSXmlBase.text(xml, "MODEL TEST", 20, 2000, tag="name")
		self._tab.currentWidget().generateXml(xml)
		xml.writeEndElement()
		xml.writeEndElement()
		xml.writeEndDocument()
		file.close()
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.wind = PFSWindow()
		icoNew = QIcon.fromTheme("document-new", QIcon())
		actNew = QAction(icoNew, "New Model", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		actNew.triggered.connect(self.wind.newPage)
		icoSave = QIcon.fromTheme("document-save", QIcon())
		actSave = QAction(icoSave, "Save Model", self)
		actSave.setShortcuts(QKeySequence.Save)
		actSave.setStatusTip("Salva o modelo em um arquivo")
		actSave.triggered.connect(self.wind.savePage)		
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