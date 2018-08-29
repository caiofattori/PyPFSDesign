from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import QFile, QIODevice, QXmlStreamWriter, QXmlStreamReader, QFileInfo, QDir, pyqtSignal
from PyQt5.QtXml import QDomDocument
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton
from page import PFSNet
from PyQt5.QtGui import QIcon, QKeySequence
from statemachine import PFSStateMachine
from xml import PFSXmlBase

class PFSWindow(QWidget):
	empty = pyqtSignal()
	nonempty = pyqtSignal()
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
		self._tab.tabCloseRequested.connect(self.closeTab)
		self._tab.setTabsClosable(True)
	
	def changeTab(self, index: int):
		if index <= 0:
			return
		net = self._tab.widget(index)
		if net._filepath is not None:
			self._lastPath = net._filepath
			
	def closeTab(self, index: int):
		self._tab.setCurrentIndex(index)
		if not self._tab.widget(index).isSaved():
			ans = QMessageBox.question(self, "Arquivo não salvo...", "Deseja salvar o arquivo antes de fechá-lo?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
			if ans == QMessageBox.Cancel:
				return
			if ans == QMessageBox.Save:
				self.saveNet()
		if self._tab.count() == 1:
			self.empty.emit()
		self._tab.removeTab(index)

			
	
	def setStateMachine(self, sm: PFSStateMachine):
		self._sm = sm
		
	def newNet(self):
		w = PFSNet.newNet("n" + str(self._idNet), self._sm)
		w.changed.connect(self.changeCurrentTabName)
		self._idNet = self._idNet + 1
		i = self._tab.addTab(w, w.getTabName())
		self._tab.setCurrentIndex(i)
		self._sm.fixTransitions(w._pages[0]._scene)
		self.nonempty.emit()
	
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
		
	def openNet(self):
		filename, filter = QFileDialog.getOpenFileName(self, "Abrir arquivo...", self._lastPath, "XML files (*.xml *.pnml)")
		if filename is None or filename == "":
			return
		if not (filename.endswith(".xml") or filename.endswith(".pnml")):
			filename = filename + ".xml"
		file = QFile(filename)
		if not file.open(QIODevice.ReadOnly):
			return
		doc = QDomDocument("PetriNetDoc")
		ans, errMsg, errLine, errColl = doc.setContent(file)
		if not ans:
			return
		nets = PFSNet.createFromXml(doc, self._sm)
		if len(nets) == 0:
			return
		self.nonempty.emit()
		for net in nets:
			f = QFileInfo(filename)
			net._filename = f.fileName()
			net._filepath = f.absolutePath()
			file.close()
			self._lastPath = net._filepath
			net.changed.connect(self.changeCurrentTabName)
			self._idNet = self._idNet + 1
			i = self._tab.addTab(net, net.getTabName())
			self._tab.setCurrentIndex(i)
		
	def changeCurrentTabName(self):
		self._tab.setTabText(self._tab.currentIndex(), self._tab.currentWidget().getTabName())
	
	def deleteElements(self):
		self._tab.currentWidget().deleteElements()
		
class PFSMain(QMainWindow):
	def __init__(self):
		super(QMainWindow, self).__init__()
		icoNew = QIcon.fromTheme("document-new", QIcon("../icons/document-new.svg"))
		actNew = QAction(icoNew, "New Model", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		icoOpen = QIcon.fromTheme("document-open", QIcon("../icons/document-open.svg"))
		actOpen = QAction(icoOpen, "Open Model", self)
		actOpen.setShortcuts(QKeySequence.Open)
		actOpen.setStatusTip("Abre um arquivo com modelo")
		icoSave = QIcon.fromTheme("document-save", QIcon("../icons/document-save.svg"))
		actSave = QAction(icoSave, "Save Model", self)
		actSave.setShortcuts(QKeySequence.Save)
		actSave.setStatusTip("Salva o modelo em um arquivo")
		self.actSave = actSave		
		toolBar = self.addToolBar("Basic")
		toolBar.addAction(actNew)
		toolBar.addAction(actOpen)
		toolBar.addAction(actSave)
		toolBar = self.addToolBar("Elements")
		self.btnActivity = PFSActivityButton()
		ac = toolBar.addWidget(self.btnActivity)
		ac.setVisible(True)
		self.btnDistributor = PFSDistributorButton()
		ac = toolBar.addWidget(self.btnDistributor)
		ac.setVisible(True)
		self.btnRelation = PFSRelationButton()
		ac = toolBar.addWidget(self.btnRelation)
		ac.setVisible(True)
		toolBar = self.addToolBar("Editing")
		icoDelete = QIcon.fromTheme("edit-delete", QIcon("../icons/edit-delete.svg"))
		actDelete = QAction(icoDelete, "Delete Element", self)
		actDelete.setShortcuts(QKeySequence.Delete)
		actDelete.setStatusTip("Remove os elementos do modelo atual")
		toolBar.addAction(actDelete)
		self.actDelete = actDelete
		icoUndo = QIcon.fromTheme("edit-undo", QIcon("../icons/edit-undo.svg"))
		actUndo = QAction(icoUndo, "Undo Command", self)
		actUndo.setShortcuts(QKeySequence.Undo)
		actUndo.setStatusTip("Desfaz última ação")
		toolBar.addAction(actUndo)
		self.actUndo = actUndo
		self.wind = PFSWindow()
		self.wind.empty.connect(self.disableButtons)
		self.wind.nonempty.connect(self.enableButtons)
		actNew.triggered.connect(self.wind.newNet)
		actOpen.triggered.connect(self.wind.openNet)
		actSave.triggered.connect(self.wind.saveNet)
		actDelete.triggered.connect(self.wind.deleteElements)
		self.setCentralWidget(self.wind)
		self.disableButtons()
		
	def setStateMachine(self, sm: PFSStateMachine):
		self.wind.setStateMachine(sm)
		
	def disableButtons(self):
		self.btnActivity.setEnabled(False)
		self.btnDistributor.setEnabled(False)
		self.btnRelation.setEnabled(False)
		self.actSave.setEnabled(False)
		self.actDelete.setEnabled(False)
		
	def enableButtons(self):
		self.btnActivity.setEnabled(True)
		self.btnDistributor.setEnabled(True)
		self.btnRelation.setEnabled(True)
		self.actSave.setEnabled(True)
		self.actDelete.setEnabled(True)

if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	win = PFSMain()
	stateMachine = PFSStateMachine(win)
	win.setStateMachine(stateMachine)
	stateMachine.start()
	win.showMaximized()
	sys.exit(app.exec_())