from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTabWidget
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QUndoStack, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QXmlStreamWriter
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtXml import QDomDocument, QDomNode
from generic import PFSNode
from element import PFSActivity, PFSDistributor, PFSRelation
from xml import PFSXmlBase
from statemachine import PFSStateMachine
from undo import *
from scene import *
from table import PFSTableLabel, PFSTableValueText, PFSTableNormal

class PFSPage(QWidget):
	def __init__(self, id: str, w: int, h: int, stateMachine: PFSStateMachine, net):
		super(QWidget, self).__init__()
		self._id = id
		self._net = net
		self._scene = PFSScene(w, h, stateMachine, self)
		self._view = PFSView(self._scene)
		layout = QVBoxLayout()
		layoutH = QHBoxLayout()
		lblWidth = QLabel("Width: ")
		layoutH.addWidget(lblWidth)
		self.txtWidth = QLineEdit(str(w))
		self.txtWidth.editingFinished.connect(self.resizeScene)
		layoutH.addWidget(self.txtWidth)
		lblHeight = QLabel("Height: ")
		layoutH.addWidget(lblHeight)
		self.txtHeight = QLineEdit(str(h))
		self.txtHeight.editingFinished.connect(self.resizeScene)
		layoutH.addWidget(self.txtHeight)
		chkPaintGrid = QCheckBox("Show grid")
		chkPaintGrid.setChecked(True)
		chkPaintGrid.stateChanged.connect(self._scene.setPaintGrid)
		layoutH.addWidget(chkPaintGrid)
		but = QPushButton("Fit page")
		but.clicked.connect(self.fitPage)
		layoutH.addWidget(but)
		layout.addLayout(layoutH)
		layout.addWidget(self._view)
		self.setLayout(layout)
		
	def generateXml(self, xml: QXmlStreamWriter):
		xml.writeStartElement("page")
		PFSXmlBase.open(xml)
		xml.writeStartElement("pagetype")
		xml.writeAttribute("mainpage", "true")
		xml.writeAttribute("id", "pg0")
		xml.writeAttribute("ref", "")
		xml.writeEndElement() #fim da pagetype
		xml.writeStartElement("pagegraphics")
		PFSXmlBase.position(xml, self.txtWidth.text(), self.txtHeight.text(), "dimension")
		xml.writeEndElement() #fim da pagegraphics
		PFSXmlBase.close(xml)
		for e in self._scene.items():
			if isinstance(e, PFSActivity) or isinstance(e, PFSDistributor) or isinstance(e, PFSRelation):
				e.generateXml(xml)
		xml.writeEndElement() #fim da page
	
	def fitPage(self):
		l = None
		r = None
		t = None
		b = None
		for e in self._scene.items():
			if isinstance(e, PFSActivity) or isinstance(e, PFSDistributor):
				rect = e.sceneBoundingRect()
				if t is None or rect.top() < t:
					t = rect.top()
				if b is None or rect.bottom() > b:
					b = rect.bottom()
				if l is None or rect.left() < l:
					l = rect.left()
				if r is None or rect.right() > r:
					r = rect.right()
		if l is not None and r is not None and t is not None and b is not None:
			x = PFSUndoRectPage(self._scene, self.txtWidth, self.txtHeight, QRect(l, t, r-l, b-t,))
			self._net.undoStack.push(x)
	
	def resizeScene(self, width=None, height=None):
		if width is None:
			width = self._scene.sceneRect().width()
		if height is None:
			height = self._scene.sceneRect().height()
		x = PFSUndoResizePage(self._scene, width, height)
		self._net.undoStack.push(x)
	
	def getTabName(self) -> str:
		if self._file is None:
			return "New_Model"
		return "New_Model"
	
	def newPage(id: str, sm: PFSStateMachine, net):
		return PFSPage(id, 4000, 4000, sm, net)
	
	def createFromXml(node: QDomNode, sm: PFSStateMachine, net):
		if node.nodeName() != "page":
			return None
		id = None
		mainpage = None
		ref = None
		width = None
		height = None
		activities = []
		distributors = []
		relations = []
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if PFSXmlBase.toolHasChild(child, "pagetype"):
				confChilds = child.childNodes()
				for j in range(confChilds.count()):
					confChild = confChilds.at(j)
					if confChild.nodeName() == "pagetype":
						if confChild.hasAttributes():
							attr = confChild.attributes()
							if attr.contains("id"):
								id = attr.namedItem("id").nodeValue()
							if attr.contains("mainpage"):
								mainpage = attr.namedItem("mainpage").nodeValue() == "true"
							if attr.contains("ref"):
								ref = attr.namedItem("ref").nodeValue()
					if confChild.nodeName() == "pagegraphics":
						graphic = PFSXmlBase.getPosition(confChild)
						if graphic is not None:
							width = graphic.x
							height = graphic.y	
			elif PFSXmlBase.toolHasChild(child, "activity"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "activity":
					activity = PFSActivity.createFromXml(confChilds.at(0))
					if activity is not None:
						activities.append(activity)
			elif PFSXmlBase.toolHasChild(child, "distributor"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "distributor":
					distributor = PFSDistributor.createFromXml(confChilds.at(0))
					if distributor is not None:
						distributors.append(distributor)
			elif PFSXmlBase.toolHasChild(child, "relation"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "relation":
					relation = PFSRelation.createFromXml(confChilds.at(0))
					if relation is not None:
						relations.append(relation)
		if id is not None and id != "" and mainpage is not None:
			if width is None:
				width = 4000
			if height is None:
				height = 4000
			page = PFSPage(id, width, height, sm, net)
			aId = []
			for activity in activities:
				page._scene.addItem(activity)
				aId.append(activity._id)
			dId = []
			for distributor in distributors:
				page._scene.addItem(distributor)
				dId.append(distributor._id)
			rId = []
			for relation in relations:
				a = 0
				d = 0
				s = None
				if aId.count(relation.source) > 0:
					s = activities[aId.index(relation.source)]
					a = a + 1
				elif dId.count(relation.source) > 0:
					s = distributors[dId.index(relation.source)]
					d = d + 1
				else:
					continue
				t = None
				if aId.count(relation.target) > 0:
					t = activities[aId.index(relation.target)]
					a = a + 1
				elif dId.count(relation.target) > 0:
					t = distributors[dId.index(relation.target)]
					d = d + 1
				else:
					continue				
				if d == 1 and a == 1:
					rel = PFSRelation.createRelation(relation.id, s, t)
					rel._midPoints = relation.midPoints
					if relation.pen is not None:
						rel._pen = relation.pen
					page._scene.addItem(rel)
					rId.append(relation.id)
			return page
		return None
	
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Page")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Largura")
		lblValue = PFSTableValueText(str(self._scene.sceneRect().width()))
		lblValue.edited.connect(self.changePageWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableValueText(str(self._scene.sceneRect().height()))
		lblValue.edited.connect(self.changePageHeight)
		ans.append([lblType, lblValue])
		return ans
	
	def changePageWidth(self, value: str):
		self.resizeScene(width=int(float(value)))
	
	def changePageHeight(self, value: str):
		self.resizeScene(height=int(float(value)))

class PFSNet(QWidget):
	changed = pyqtSignal()
	def __init__(self, id: str, sm: PFSStateMachine):
		super(QWidget, self).__init__()
		self._filename = None
		self._filepath = None
		self._id = id
		self._layout = QHBoxLayout()
		self._tab = QTabWidget()
		self.setLayout(self._layout)
		self._prop = QTableWidget(20, 2)
		self._prop.itemChanged.connect(self.propertiesItemChanged)
		self._prop.verticalHeader().hide()
		self._pages = []
		self._idPage = 0
		self._sm = sm
		self._distributorId = 0
		self._activityId = 0
		self._relationId = 0
		self.undoStack = QUndoStack(self)
		self.undoAction = self.undoStack.createUndoAction(self, "Desfazer")
		self.undoAction.setShortcuts(QKeySequence.Undo)
		self.undoAction.setIcon(QIcon.fromTheme("edit-undo", QIcon("../icons/edit-undo.svg")))
		self.redoAction = self.undoStack.createRedoAction(self, "Refazer")
		self.redoAction.setShortcuts(QKeySequence.Redo)
		self.redoAction.setIcon(QIcon.fromTheme("edit-redo", QIcon("../icons/edit-redo.svg")))
		
	def propertiesItemChanged(self, item: PFSTableValueText):
		if item.comparePrevious():
			item.edited.emit(item.value())
		
	def generateXml(self, xml: QXmlStreamWriter):
		xml.writeStartDocument()
		xml.writeStartElement("PetriNetDoc")
		xml.writeStartElement("net")
		xml.writeAttribute("id", self._id)
		for p in self._pages:
			p.generateXml(xml)
		xml.writeEndElement()
		xml.writeEndElement()
		xml.writeEndDocument()
	
	def createFromXml(doc: QDomDocument, sm: PFSStateMachine):
		el = doc.documentElement()
		nodes = el.childNodes()
		nets = []
		for i in range(nodes.count()):
			node = nodes.at(i)
			if node.nodeName() != "net":
				continue
			if not (node.hasAttributes() and node.attributes().contains("id")):
				continue
			id = node.attributes().namedItem("id").nodeValue()
			net = PFSNet(id, sm)
			nodesPage = node.childNodes()
			pages = []
			for j in range(nodesPage.count()):
				nodePage = nodesPage.at(j)
				if nodePage.nodeName() != "page":
					continue
				page = PFSPage.createFromXml(nodePage, sm, net)
				if page is not None:
					pages.append(page)
			if len(pages) > 0:
				net._pages = pages
				net._layout.addWidget(pages[0])
				net._layout.addWidget(net._prop)
				nets.append(net)
		return nets	
	
	def getTabName(self) -> str:
		if self._filename is None:
			ans = "New model"
		else:
			ans = self._filename
		if self.undoStack.isClean():
			return ans
		return ans + "*"
		
	def newNet(id, sm: PFSStateMachine):
		ans = PFSNet(id, sm)
		page = PFSPage.newPage("pg" + str(ans._idPage), sm, ans)
		ans._idPage = ans._idPage + 1
		ans._pages.append(page)
		ans._layout.addWidget(page)
		ans._layout.addWidget(ans._prop)
		return ans
		
	def deleteElements(self):
		if len(self._pages) > 1:
			scene = self._tab.currentWidget()._scene
		elif len(self._pages) == 1:
			scene = self._pages[0]._scene
		scene._itemsDeleted = scene.selectedItems()
		for item in scene._itemsDeleted:
			if isinstance(item, PFSNode):
				item.deleted.emit()
		x = PFSUndoDelete(scene._itemsDeleted)
		self.undoStack.push(x)