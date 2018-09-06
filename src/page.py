from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTabWidget
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QUndoStack, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QXmlStreamWriter, QSize
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtXml import QDomDocument, QDomNode
from generic import PFSNode
from element import PFSActivity, PFSDistributor, PFSRelation, PFSOpenActivity, PFSCloseActivity
from xml import PFSXmlBase
from statemachine import PFSStateMachine
from undo import *
from scene import *
from table import PFSTableLabel, PFSTableValueText, PFSTableNormal, PFSTableValueCheck
from image import PFSImage
from generic import PFSActive, PFSPassive

class PFSPage(QWidget):
	def __init__(self, id: str, w: int, h: int, stateMachine: PFSStateMachine, net):
		super(QWidget, self).__init__()
		self._id = id
		self._net = net
		self._scene = PFSScene(w, h, stateMachine, self)
		self._view = PFSView(self._scene)
		layout = QVBoxLayout()
		layout.addWidget(self._view)
		self.setLayout(layout)
		self._subRef = None
		self._name = "Principal"
	
	def setName(self, txt):
		self._name = txt
	
	def name(self):
		return self._name
	
	def generateXml(self, xml: QXmlStreamWriter):
		xml.writeStartElement("page")
		PFSXmlBase.open(xml)
		xml.writeStartElement("pagetype")
		xml.writeAttribute("id", self._id)
		if self._subRef is None:
			xml.writeAttribute("mainpage", "true")
			xml.writeAttribute("ref", "")
		else:
			xml.writeAttribute("mainpage", "false")
			xml.writeAttribute("ref", self._subRef)
		xml.writeEndElement() #fim da pagetype
		xml.writeStartElement("pagegraphics")
		PFSXmlBase.position(xml, str(self._scene.width()), str(self._scene.height()), "dimension")
		xml.writeEndElement() #fim da pagegraphics
		PFSXmlBase.close(xml)
		for e in self._scene.items():
			if isinstance(e, PFSActive) or isinstance(e, PFSPassive) or isinstance(e, PFSRelation):
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
			x = PFSUndoRectPage(self._scene, QRect(l, t, r-l, b-t,))
			self._net.undoStack.push(x)
	
	def resizeScene(self, width=None, height=None):
		if width is None:
			width = self._scene.sceneRect().width()
		if height is None:
			height = self._scene.sceneRect().height()
		self._scene.resize(int(float(width)), int(float(height)))
	
	def getTabName(self) -> str:
		if self._file is None:
			return "New_Model"
		return "New_Model"
	
	def newPage(id: str, sm: PFSStateMachine, net, width = 4000, height = 4000):
		return PFSPage(id, width, height, sm, net)
	
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
	
	def getAllSubPages(self):
		ans = []
		for e in self._scene.items():
			if isinstance(e, PFSActivity):
				if e.hasSubPage():
					ans.append(e.subPage())
					aux = e.subPage().getAllSubPages()
					if len(aux) > 0:
						ans = ans + aux
		return ans
	
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
		lblType = PFSTableLabel("Mostra grid")
		lblValue = PFSTableValueCheck("", self._scene._paintGrid)
		lblValue.stateChanged.connect(self._scene.setPaintGrid)
		ans.append([lblType, lblValue])		
		return ans
	
	def changePageWidth(self, prop):
		x = PFSUndoPropertyText(prop, self.resizeWidth)
		self._net.undoStack.push(x)
		
	def changePageHeight(self, prop):
		x = PFSUndoPropertyText(prop, self.resizeHeight)
		self._net.undoStack.push(x)

	def resizeWidth(self, txt):	
		self.resizeScene(width=int(float(txt)))
		
	def resizeHeigh(self, txt):	
		self.resizeScene(height=int(float(txt)))	

class PFSNet(QWidget):
	changed = pyqtSignal()
	def __init__(self, id: str, sm: PFSStateMachine):
		super(QWidget, self).__init__()
		self._filename = None
		self._filepath = None
		self._id = id
		layout = QHBoxLayout()
		self._tab = QTabWidget()
		layout.addWidget(self._tab)
		self.setLayout(layout)
		self._prop = QTableWidget(20, 2)
		self._prop.itemChanged.connect(self.propertiesItemChanged)
		self._prop.verticalHeader().hide()
		layout.addWidget(self._prop)
		self._pages = []
		self._idPage = 0
		self._sm = sm
		self._distributorId = 0
		self._activityId = 0
		self._relationId = 0
		self._otherId = 0
		self._pageId = 0
		self._page = None
		self._elements = {}
		self.undoStack = QUndoStack(self)
		self.undoAction = self.undoStack.createUndoAction(self, "Desfazer")
		self.undoAction.setShortcuts(QKeySequence.Undo)
		self.undoAction.setIcon(QIcon.fromTheme("edit-undo", QIcon("../icons/edit-undo.svg")))
		self.redoAction = self.undoStack.createRedoAction(self, "Refazer")
		self.redoAction.setShortcuts(QKeySequence.Redo)
		self.redoAction.setIcon(QIcon.fromTheme("edit-redo", QIcon("../icons/edit-redo.svg")))
		
	def propertiesItemChanged(self, item: PFSTableValueText):
		if item.comparePrevious():
			item.edited.emit(item)
	
	def getAllPages(self):
		ans = []
		ans.append(self._page)
		aux = self._page.getAllSubPages()
		if len(aux) > 0:
			ans = ans + aux
		return ans
	
	def generateXml(self, xml: QXmlStreamWriter):
		xml.writeStartDocument()
		xml.writeStartElement("PetriNetDoc")
		xml.writeStartElement("net")
		xml.writeAttribute("id", self._id)
		pages = self.getAllPages()
		for p in pages:
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
		page = PFSPage.newPage(ans.requestId(PFSPage), sm, ans)
		ans._page = page
		ans._pages.append(page)
		ans._tab.addTab(page, page.name())
		return ans
	
	def openPage(self, element):
		if isinstance(element, PFSPage):
			page = element
		elif isinstance(element, PFSActivity):
			page = element.subPage()
		else:
			return
		if page not in self._pages:
			self._tab.addTab(page, page.name())
			self._pages.append(page)
		self._tab.setCurrentWidget(page)
	
	def createPage(self, element=None):
		page = PFSPage.newPage(self.requestId(PFSPage), self._sm, self, 600, 120)
		if element is not None and element.setSubPage(page):
			page.setName("Ref_" + element._id)
			page._subRef = element._id
			openac = PFSOpenActivity(self.requestId(PFSOpenActivity), 20, 10, 100, element)
			self.addItemNoUndo(openac, page)
			closeac = PFSCloseActivity(self.requestId(PFSCloseActivity), page._scene.sceneRect().width()-20, 10, 100, element)
			self.addItemNoUndo(closeac, page)
			self._idPage = self._idPage + 1
			self._sm.fixTransitions(page._scene)
			return page
		return None
		
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
		
	def export(self, filename):
		if len(self._pages) > 1:
			scene = self._tab.currentWidget()._scene
		elif len(self._pages) == 1:
			scene = self._pages[0]._scene
		else:
			return
		if filename.endswith(".png"):
			PFSImage.gravaPng(scene, filename)
		else:
			PFSImage.gravaSvg(scene, filename)
	
	def addItem(self, element, page:PFSPage):
		if isinstance(element, PFSRelation):
			if isinstance(element._source, PFSActive) and isinstance(element._target, PFSActive):
				return False
			if isinstance(element._source, PFSPassive) and isinstance(element._target, PFSPassive):
				return False
		x = PFSUndoAdd([element], page._scene)
		self.undoStack.push(x)
		return True
	
	def addItemNoUndo(self, element, page:PFSPage):
		if isinstance(element, PFSRelation):
			if isinstance(element._source, PFSActive) and isinstance(element._target, PFSActive):
				return False
			if isinstance(element._source, PFSPassive) and isinstance(element._target, PFSPassive):
				return False
		page._scene.addItem(element)
		page._scene.update()
		return True	
	
	def requestId(self, element):
		if element == PFSActivity:
			ans = "A" + str(self._activityId)
			self._activityId = self._activityId + 1
		elif element == PFSDistributor:
			ans = "D" + str(self._distributorId)
			self._distributorId = self._distributorId + 1
		elif element == PFSRelation:
			ans = "R" + str(self._relationId)
			self._relationId = self._relationId + 1
		elif element == PFSPage:
			ans = "P" + str(self._pageId)
			self._pageId = self._pageId + 1
		else:
			ans = "O" + str(self._otherId)
			self._otherId = self._otherId + 1
		return ans