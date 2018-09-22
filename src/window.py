from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QToolBar, QMainWindow, QTabWidget, QAction, QFileDialog, QMessageBox, QMenu
from PyQt5.QtCore import QFile, QIODevice, QXmlStreamWriter, QXmlStreamReader, QFileInfo, QDir, pyqtSignal, QTimer, QRect
from PyQt5.QtXml import QDomDocument
from toolbutton import PFSActivityButton, PFSDistributorButton, PFSRelationButton, PFSSecondaryFlowButton
from page import PFSNet
from PyQt5.QtGui import QIcon, QKeySequence
from statemachine import PFSStateMachine
from xml import PFSXmlBase
from element import PFSDistributor, PFSActivity
from relation import *

class PFSWindow(QWidget):
	empty = pyqtSignal()
	nonempty = pyqtSignal()
	def __init__(self, main:QMainWindow):
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
		self._main = main
		timer = QTimer(self)
		timer.timeout.connect(self.autoSave)
		timer.start(30000)
		self._bufferElements = []
		self._pasteRect = None
	
	def changeTab(self, index: int):
		if index < 0:
			return
		self._main.tabChanged.emit()
		net = self._tab.widget(index)
		net._tab.currentWidget()._scene.clearSelection()
		self.updateUndoRedoAction()
		if net._filepath is not None:
			self._lastPath = net._filepath
	
	def prepareCloseTab(self, index: int):
		if not self._tab.widget(index).undoStack.isClean():
			ans = QMessageBox.question(self, "Arquivo não salvo...", "Deseja salvar o arquivo antes de fechá-lo?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
			if ans == QMessageBox.Cancel:
				return False
			if ans == QMessageBox.Save:
				if not self.saveNet():
					return False
		return True
	
	def closeTab(self, index: int):
		self._tab.setCurrentIndex(index)
		if not self._tab.widget(index).undoStack.isClean():
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
		w = PFSNet.newNet("n" + str(self._idNet), self)
		w.undoStack.cleanChanged.connect(self.changeCurrentTabName)
		self._idNet = self._idNet + 1
		i = self._tab.addTab(w, w.getTabName())
		self._tab.setCurrentIndex(i)
		self._sm.fixTransitions(w._pages[0]._scene)
		self.nonempty.emit()
		if self._tab.count() == 1:
			self.updateUndoRedoAction()
	
	def saveFile(self, net, filepath, filename):
		file = QFile(QFileInfo(QDir(filepath), filename).absoluteFilePath())
		file.open(QIODevice.WriteOnly)
		xml = QXmlStreamWriter(file)
		net.generateXml(xml)
		file.close()
		
	def autoSave(self):
		for i in range(self._tab.count()):
			net = self._tab.widget(i)
			if net.undoStack.isClean():
				continue
			if net._filename is None:
				filename = "newmodel.xml~"
				filepath = self._lastPath
			else:
				filename = net._filename + "~"
				filepath = net._filepath
			self.saveFile(net, filepath, filename)
	
	def saveAsNet(self):
		net = self._tab.currentWidget()
		filename, filter = QFileDialog.getSaveFileName(self, "Salvar arquivo como...", self._lastPath, "XML files (*.xml *.pnml)")
		if filename is None or not filename:
			return
		if not (filename.endswith(".xml") or filename.endswith(".pnml")):
			filename = filename + ".xml"
		f = QFileInfo(filename)
		net._filename = f.fileName()
		net._filepath = f.absolutePath()
		self.saveFile(net, net._filepath, net._filename)
		net.undoStack.setClean()
		self._lastPath = net._filepath
	
	def saveNet(self):
		net = self._tab.currentWidget()
		if net._filename is None:
			filename, filter = QFileDialog.getSaveFileName(self, "Salvar arquivo...", self._lastPath, "XML files (*.xml *.pnml)")
			if filename is None or not filename:
				return False
			if not (filename.endswith(".xml") or filename.endswith(".pnml")):
				filename = filename + ".xml"
			f = QFileInfo(filename)
			net._filename = f.fileName()
			net._filepath = f.absolutePath()
		self.saveFile(net, net._filepath, net._filename)
		net.undoStack.setClean()
		self._lastPath = net._filepath
		return True
		
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
		nets = PFSNet.createFromXml(doc, self)
		if len(nets) == 0:
			return
		self.nonempty.emit()
		for net in nets:
			f = QFileInfo(filename)
			net._filename = f.fileName()
			net._filepath = f.absolutePath()
			file.close()
			self._lastPath = net._filepath
			net.undoStack.cleanChanged.connect(self.changeCurrentTabName)
			self._idNet = self._idNet + 1
			i = self._tab.addTab(net, net.getTabName())
			self._tab.setCurrentIndex(i)
			if self._tab.count() == 1:
				self.updateUndoRedoAction()
			self._sm.fixTransitions(net._pages[0]._scene)
	
	def updateUndoRedoAction(self):
		self._main.undoToolBar.clear()
		self._main.editMenu.clear()
		self._main.undoToolBar.addAction(self._tab.currentWidget().undoAction)
		self._main.undoToolBar.addAction(self._tab.currentWidget().redoAction)
		self._main.editMenu.addAction(self._tab.currentWidget().undoAction)
		self._main.editMenu.addAction(self._tab.currentWidget().redoAction)
		self._main.editMenu.addSeparator()
		self._main.editMenu.addAction(self._main.actCopy)
		self._main.editMenu.addAction(self._main.actPaste)
		self._main.editMenu.addAction(self._main.actDelete)
		
	
	def changeCurrentTabName(self, value):
		self._tab.setTabText(self._tab.currentIndex(), self._tab.currentWidget().getTabName())
	
	def deleteElements(self):
		self._tab.currentWidget().deleteElements()
		
	def exportNet(self):
		filename, filter = QFileDialog.getSaveFileName(self, "Exportar arquivo...", self._lastPath, "SVG files (*.svg);; PNG files (*.png)")
		if filename is None or filename == "":
			return
		if not (filename.endswith(".svg") or filename.endswith(".png")):
			filename = filename + ".svg"
		self._tab.currentWidget().export(filename)
	
	def copyElements(self):
		aux = self._tab.currentWidget()._tab.currentWidget()._scene.selectedItems()
		x = self._tab.currentWidget()._tab.currentWidget()._scene.sceneRect().right()
		y = self._tab.currentWidget()._tab.currentWidget()._scene.sceneRect().bottom()
		xw = self._tab.currentWidget()._tab.currentWidget()._scene.sceneRect().left()
		yh = self._tab.currentWidget()._tab.currentWidget()._scene.sceneRect().top()
		if len(aux) > 0:
			for elem in aux:
				if not (isinstance(elem, PFSActivity) or isinstance(elem, PFSDistributor)):
					continue
				if x > elem._x:
					x = elem._x
				if y > elem._y:
					y = elem._y
			self._bufferElements = []
			for elem in aux:
				if isinstance(elem, PFSRelation) and not(elem._source in aux and elem._target in aux):
					continue
				self._bufferElements.append(elem.copy(x, y))
	
	def pasteElements(self):
		if len(self._bufferElements) > 0:
			self._tab.currentWidget().pasteElements(self._bufferElements)
			self._main.paste.emit()
	
	def quit(self):
		for i in range(self._tab.count()):
			if not self.prepareCloseTab(i):
				return False
		return True
		
class PFSMain(QMainWindow):
	tabChanged = pyqtSignal()
	paste = pyqtSignal()
	def __init__(self):
		super(QMainWindow, self).__init__()
		icoNew = QIcon.fromTheme("document-new", QIcon("icons/document-new.svg"))
		actNew = QAction(icoNew, "Novo", self)
		actNew.setShortcuts(QKeySequence.New)
		actNew.setStatusTip("Cria um novo arquivo de modelo")
		icoOpen = QIcon.fromTheme("document-open", QIcon("icons/document-open.svg"))
		actOpen = QAction(icoOpen, "Abrir", self)
		actOpen.setShortcuts(QKeySequence.Open)
		actOpen.setStatusTip("Abre um arquivo com modelo")
		icoSave = QIcon.fromTheme("document-save", QIcon("icons/document-save.svg"))
		actSave = QAction(icoSave, "Salvar", self)
		actSave.setShortcuts(QKeySequence.Save)
		actSave.setStatusTip("Salva o modelo em um arquivo")
		self.actSave = actSave
		icoSaveAs = QIcon.fromTheme("document-save-as", QIcon("icons/document-save-as.svg"))
		actSaveAs = QAction(icoSaveAs, "Salvar Como", self)
		actSaveAs.setShortcuts(QKeySequence.SaveAs)
		actSaveAs.setStatusTip("Salva como o modelo em um arquivo")
		self.actSaveAs = actSaveAs
		icoExport = QIcon.fromTheme("insert-image", QIcon("icons/document-export.svg"))
		actExport = QAction(icoExport, "Exportar", self)
		actExport.setShortcuts(QKeySequence.Print)
		actExport.setStatusTip("Exporta o modelo como figura")
		self.actExport = actExport
		icoQuit = QIcon.fromTheme("application-exit", QIcon("icons/application-exit.svg"))
		actQuit = QAction(icoQuit, "Sair", self)
		actQuit.setShortcuts(QKeySequence.Quit)
		actQuit.setStatusTip("Sair do programa")
		self.actQuit = actQuit		
		toolBar = self.addToolBar("Basic")
		toolBar.addAction(actNew)
		toolBar.addAction(actOpen)
		toolBar.addAction(actSave)
		toolBar.addAction(actSaveAs)
		toolBar.addAction(actExport)
		fileMenu = self.menuBar().addMenu("Arquivo")
		fileMenu.addAction(actNew)
		fileMenu.addAction(actOpen)
		fileMenu.addAction(actSave)
		fileMenu.addAction(actSaveAs)
		fileMenu.addSeparator()
		fileMenu.addAction(actExport)
		fileMenu.addSeparator()
		fileMenu.addAction(actQuit)
		editMenu = self.menuBar().addMenu("Editar")
		self.editSeparator = editMenu.addSeparator()
		toolBar = self.addToolBar("Edit")
		icoCopy = QIcon.fromTheme("edit-copy", QIcon("icons/edit-copy.svg"))
		actCopy = QAction(icoCopy, "Copia Elementos", self)
		actCopy.setShortcuts(QKeySequence.Copy)
		actCopy.setStatusTip("Copia elementos do modelo")
		self.actCopy = actCopy
		toolBar.addAction(actCopy)
		icoPaste = QIcon.fromTheme("edit-paste", QIcon("icons/edit-paste.svg"))
		actPaste = QAction(icoPaste, "Cola Elementos", self)
		actPaste.setShortcuts(QKeySequence.Paste)
		actPaste.setStatusTip("Cola elementos do modelo")
		self.actPaste = actPaste
		toolBar.addAction(actPaste)
		icoDelete = QIcon.fromTheme("edit-delete", QIcon("icons/edit-delete.svg"))
		actDelete = QAction(icoDelete, "Apaga Elementos", self)
		actDelete.setShortcuts(QKeySequence.Delete)
		actDelete.setStatusTip("Remove os elementos do modelo atual")
		toolBar.addAction(actDelete)
		self.actDelete = actDelete
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
		self.btnSecFlow = PFSSecondaryFlowButton()
		sf = toolBar.addWidget(self.btnSecFlow)
		sf.setVisible(True)
		self.undoToolBar = self.addToolBar("Undo-Redo")
		editMenu.addAction(actCopy)
		editMenu.addAction(actPaste)
		editMenu.addAction(actDelete)
		self.editMenu = editMenu
		self.wind = PFSWindow(self)
		self.wind.empty.connect(self.disableButtons)
		self.wind.nonempty.connect(self.enableButtons)
		actNew.triggered.connect(self.wind.newNet)
		actOpen.triggered.connect(self.wind.openNet)
		actSave.triggered.connect(self.wind.saveNet)
		actSaveAs.triggered.connect(self.wind.saveAsNet)
		actExport.triggered.connect(self.wind.exportNet)
		actQuit.triggered.connect(self.quit)
		actDelete.triggered.connect(self.wind.deleteElements)
		actCopy.triggered.connect(self.wind.copyElements)
		actPaste.triggered.connect(self.wind.pasteElements)
		self.setCentralWidget(self.wind)
		self.disableButtons()
		#self.disableEdits()
		
	def setStateMachine(self, sm: PFSStateMachine):
		self.wind.setStateMachine(sm)
	
	def disableEdits(self):
		self.actCopy.setEnabled(False)
		self.actDelete.setEnabled(False)
	
	def quit(self):
		self.close()
	
	def closeEvent(self, ev):
		if self.wind.quit():
			self.close()		
	
	def disableButtons(self):
		self.btnActivity.setEnabled(False)
		self.btnDistributor.setEnabled(False)
		self.btnRelation.setEnabled(False)
		self.actSave.setEnabled(False)
		self.actSaveAs.setEnabled(False)
		self.actExport.setEnabled(False)
		
		
	def enableButtons(self):
		self.btnActivity.setEnabled(True)
		self.btnDistributor.setEnabled(True)
		self.btnRelation.setEnabled(True)
		self.actSave.setEnabled(True)
		self.actSaveAs.setEnabled(True)
		self.actExport.setEnabled(True)
		self.actDelete.setEnabled(True)

if __name__ == "__main__":
	import sys
	try:
		app
	except:
		app = QApplication(sys.argv)
	win = PFSMain()
	stateMachine = PFSStateMachine(win)
	win.setStateMachine(stateMachine)
	stateMachine.start()
	win.showMaximized()
	sys.exit(app.exec_())