from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTabWidget, QTreeWidget, QTreeWidgetItem
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QUndoStack, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QXmlStreamWriter, QSize
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtXml import QDomDocument, QDomNode
from generic import PFSNode, PFSBasicElement
from element import PFSActivity, PFSDistributor, PFSOpenActivity, PFSCloseActivity
from xml import PFSXmlBase
from statemachine import PFSStateMachine
from undo import *
from scene import *
from table import PFSTableLabel, PFSTableValueText, PFSTableNormal, PFSTableValueCheck, PFSTableLabelTags, PFSTableValueBox
from image import PFSImage, PFSPageIcon
from generic import PFSActive, PFSPassive
from tree import PFSTreeItem
from contents import *
from relation import *

class PFSPage(PFSBasicElement, QWidget):
	clicked = pyqtSignal()
	def __init__(self, id: str, w: int, h: int, stateMachine: PFSStateMachine, net):
		PFSBasicElement.__init__(self, id)
		QWidget.__init__(self)
		self._id = id
		self._net = net
		self._scene = PFSScene(w, h, stateMachine, self)
		self._view = PFSView(self._scene)
		layout = QVBoxLayout()
		layout.addWidget(self._view)
		self.setLayout(layout)
		self._subRef = None
		self._name = "Principal"
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSPageIcon()))
		tree.clicked.connect(self.selectSingle)		
		for elem in self._scene.items():
			child = elem.tree(tree)
		return tree
	
	def selectSingle(self):
		self._net.showPage(self)
		self._scene.clearSelection()
		self._net.fillProperties(self.propertiesTable())	
	
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
			xml.writeAttribute("ref", self._subRef._id)
		xml.writeEndElement() #fim da pagetype
		xml.writeStartElement("pagegraphics")
		PFSXmlBase.position(xml, str(self._scene.width()), str(self._scene.height()), "dimension")
		xml.writeEndElement() #fim da pagegraphics
		PFSBasicElement.generateXml(self, xml)
		PFSXmlBase.close(xml)
		for e in self._scene.items():
			if isinstance(e, PFSActive) or isinstance(e, PFSPassive) or isinstance(e, PFSRelation):
				e.generateXml(xml)
		xml.writeEndElement() #fim da page
	
	def getElementById(self, id):
		for elem in self._scene.items():
			if elem._id == id:
				return elem
		return None
	
	# Temporary solution for id when load files
	def getMaxIds(self):
		a = -1
		d = -1
		r = -1
		o = -1
		for elem in self._scene.items():
			t = elem._id[0]
			n = int(elem._id[1:])
			if t == "A" and n > a:
				a = n
			if t == "D" and n > d:
				d = n
			if t == "R" and n > r:
				r = n
			if t == "O" and n > o:
				o = n
		return [a, d, r, o]
	
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
	
	def resizeScene(self, width=0, height=0):
		width = self._scene.sceneRect().width() + width
		height = self._scene.sceneRect().height() + height
		self._scene.resize(int(float(width)), int(float(height)))
	
	def newPage(id: str, sm: PFSStateMachine, net, width = 600, height = 120):
		return PFSPage(id, width, height, sm, net)
	
	def createFromXml(node: QDomNode):
		if node.nodeName() != "page":
			return None
		id = None
		mainpage = None
		ref = None
		width = None
		height = None
		activities = []
		openactivities = []
		closeactivities = []
		distributors = []
		relations = []
		childs = node.childNodes()
		tags = []
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
						for k in range(confChild.childNodes().count()):
							graph = confChild.childNodes().at(k)
							if graph.nodeName() == "dimension":
								graphic = PFSXmlBase.getPosition(graph)
								if graphic is not None:
									width = graphic.x
									height = graphic.y
					if confChild.nodeName() == "tags":
						tags = PFSBasicElement.createFromXml(confChild)
			elif PFSXmlBase.toolHasChild(child, "activity"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "activity":
					activity = PFSActivity.createFromXml(confChilds.at(0))
					if activity is not None:
						activities.append(activity)
			elif PFSXmlBase.toolHasChild(child, "openactivity"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "openactivity":
					openactivity = PFSOpenActivity.createFromXml(confChilds.at(0))
					if openactivity is not None:
						openactivities.append(openactivity)
			elif PFSXmlBase.toolHasChild(child, "closeactivity"):
				confChilds = child.childNodes()
				if confChilds.at(0).nodeName() == "closeactivity":
					closeactivity = PFSCloseActivity.createFromXml(confChilds.at(0))
					if closeactivity is not None:
						closeactivities.append(closeactivity)
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
				width = 600
			if height is None:
				height = 120
			page = PFSPageContent()
			page._id = id
			page._width = width
			page._height = height
			page._tags = tags
			page._ref = ref
			page._openActivities = openactivities
			page._closeActivities = closeactivities
			page._activities = activities
			page._distributors = distributors
			page._relations = relations
			return page
		return None
	
	def createFromContent(content: PFSPageContent, sm, net):
		page = PFSPage(content._id, content._width, content._height, sm, net)
		for tag in content._tags:
			page.addTag(tag._name, tag._use)
		items = {}
		for item in content._openActivities:
			it = PFSOpenActivity(item._id, item._x, item._y, item._h)
			for tag in item._tags:
				it.addTag(tag._name, tag._use, False)
			items[item._id] = it
		for item in content._closeActivities:
			it = PFSCloseActivity(item._id, item._x, item._y, item._h)
			for tag in item._tags:
				it.addTag(tag._name, tag._use, False)
			items[item._id] = it
		for item in content._activities:
			it = PFSActivity(item._id, item._x, item._y, item._text)
			it._brush = item._brush
			it._pen = item._pen
			it._textFont = item._textFont
			it._fontMetrics = item._fontMetrics
			it._height = item._height
			it._width = item._width
			it._inputNum = item._inputNum
			it._outputNum = item._outputNum
			for tag in item._tags:
				it.addTag(tag._name, tag._use, False)
			items[item._id] = it
		for item in content._distributors:
			it = PFSDistributor(item._id, item._x, item._y)
			it._brush = item._brush
			it._pen = item._pen
			it._height = item._height
			it._width = item._width
			for tag in item._tags:
				it.addTag(tag._name, tag._use, False)
			items[item._id] = it
		for item in content._relations:
			source = items[item._source]
			target = items[item._target]
			if (isinstance(source, PFSActive) and isinstance(target, PFSPassive)) or (isinstance(source, PFSPassive) and isinstance(target, PFSActive)):
				it = PFSRelation.createRelation(item._id, source, target)
				it._sourceNum = item._sourceNum
				it._targetNum = item._targetNum
				it._midPoints = item._midPoints
				it.updatePoints()
				it._pen = item._pen
				for tag in item._tags:
					it.addTag(tag._name, tag._use, False)				
				items[item._id] = it
		for i, item in items.items():
			page._scene.addItem(item)
		return page
	
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
		lblValue = PFSTableNormal(str(self._scene.sceneRect().width()))
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Altura")
		lblValue = PFSTableNormal(str(self._scene.sceneRect().height()))
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Redimen. esquerda")
		lblValue = PFSTableValueText("")
		lblValue.edited.connect(self.changePageWidthLeft)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Redimen. direita")
		lblValue = PFSTableValueText("")
		lblValue.edited.connect(self.changePageWidthRight)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Redimen. cima")
		lblValue = PFSTableValueText("")
		lblValue.edited.connect(self.changePageHeightTop)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Redimen. baixo")
		lblValue = PFSTableValueText("")
		lblValue.edited.connect(self.changePageHeightBottom)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Mostra grid")
		lblValue = PFSTableValueCheck("", self._scene._paintGrid)
		lblValue.stateChanged.connect(self._scene.setPaintGrid)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabelTags("Tags")
		lblValue = PFSTableValueBox(self._tags, self.createTag)
		ans.append([lblType, lblValue])		
		return ans
	
	def changePageWidthLeft(self, prop):
		try:
			a = float(prop.text())
			x = PFSUndoPropertyTextSimetric(prop, self.resizeWidthLeft)
			self._net.undoStack.push(x)
		except:
			pass
		
	def changePageWidthRight(self, prop):
		try:
			a = float(prop.text())
			x = PFSUndoPropertyTextSimetric(prop, self.resizeWidthRight)
			self._net.undoStack.push(x)
		except:
			pass
		
	def changePageHeightTop(self, prop):
		try:
			a = float(prop.text())
			x = PFSUndoPropertyTextSimetric(prop, self.resizeHeightTop)
			self._net.undoStack.push(x)
		except:
			pass
	
	def changePageHeightBottom(self, prop):
		try:
			a = float(prop.text())		
			x = PFSUndoPropertyTextSimetric(prop, self.resizeHeightBottom)
			self._net.undoStack.push(x)
		except:
			pass

	def resizeWidthLeft(self, txt):
		rel = []
		for item in self._scene.items():
			item.moveX(txt, False)
			if isinstance(item, PFSRelation):
				rel.append(item)
		for r in rel:
			r.updatePoints()
		self.resizeScene(width=int(float(txt)))

	def resizeWidthRight(self, txt):	
		self.resizeScene(width=int(float(txt)))
	
	def resizeHeightTop(self, txt):
		rel = []
		for item in self._scene.items():
			item.moveY(txt, False)
			if isinstance(item, PFSRelation):
				rel.append(item)
		for r in rel:
			r.updatePoints()
		self.resizeScene(height=int(float(txt)))	
	
	def resizeHeightBottom(self, txt):
		self.resizeScene(height=int(float(txt)))
	
	def createTag(self):
		PFSBasicElement.createTag(self, self._net)
	
	def deleteTag(self, tag):
		x = PFSUndoRemoveTag(self, tag)
		self._net.undoStack.push(x)
	
	def removeTag(self, name, use):
		PFSBasicElement.removeTag(self, name, use)
		self._net.fillProperties(self.propertiesTable())
	
	def addTag(self, name, use):
		PFSBasicElement.addTag(self, name, use)
		self._net.fillProperties(self.propertiesTable())

class PFSNet(QWidget):
	changed = pyqtSignal()
	def __init__(self, id: str, window):
		super(QWidget, self).__init__()
		self._filename = None
		self._filepath = None
		self._id = id
		layout = QHBoxLayout()
		self._tab = QTabWidget()
		self._tab.currentChanged.connect(self.changeTab)
		self._tab.setTabsClosable(True)
		self._tab.tabCloseRequested.connect(self.closeTab)
		layout.addWidget(self._tab)
		self.setLayout(layout)
		self._prop = QTableWidget(20, 2)
		self._prop.itemChanged.connect(self.propertiesItemChanged)
		self._prop.verticalHeader().hide()
		self._prop.setColumnWidth(1, 180)
		self._prop.setMaximumWidth(300)
		lv = QVBoxLayout()
		lv.addWidget(self._prop)
		self._tree = QTreeWidget()
		self._tree.itemClicked.connect(self.treeItemClicked)
		self._tree.setMaximumWidth(300)
		lv.addWidget(self._tree)
		layout.addLayout(lv)
		self._pages = []
		self._idPage = 0
		self._sm = window._sm
		self._window = window
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
		self._pasteList = []
		
	def tree(self):
		tree = QTreeWidgetItem(self._tree, ["Net " + self._id], 0)
		child = self._page.tree(tree)
		self._tree.expandAll()
		return tree
		
	def prepareTree(self):
		self._tree.clear()
		self.tree()
		
	def showPage(self, widget):
		if widget in self._pages:
			self._tab.setCurrentWidget(widget)
		else:
			self._tab.addTab(widget, widget.name())
			self._pages.append(widget)
			self._tab.setCurrentWidget(widget)
		
		
	def removeTabWidget(self, widget):
		for i in range(self._tab.count()):
			if self._tab.widget(i) == widget:
				self._tab.removeTab(i)
				self._pages.remove(widget)
		
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
		
	def treeItemClicked(self, item, col):
		if isinstance(item, PFSTreeItem):
			item.clicked.emit()
	
	def createFromXml(doc: QDomDocument, window):
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
			net = PFSNet(id, window)
			nodesPage = node.childNodes()
			pages = []
			for j in range(nodesPage.count()):
				nodePage = nodesPage.at(j)
				if nodePage.nodeName() != "page":
					continue
				page = PFSPage.createFromXml(nodePage)
				if page is not None:
					pages.append(page)
			if len(pages) == 0:
				continue
			aux = {}
			for page in pages:
				p = PFSPage.createFromContent(page, window._sm, net)
				if p is not None:
					i = page._ref
					if i is None or not i:
						i = "main"
					aux[i] = p
			if "main" not in aux.keys():
				continue
			for indice, page in aux.items():
				ids = page.getMaxIds()
				if net._activityId < ids[0] + 1:
					net._activityId = ids[0] + 1
				if net._distributorId < ids[1] + 1:
					net._distributorId = ids[1] + 1
				if net._relationId < ids[2] + 1:
					net._relationId = ids[2] + 1
				if net._otherId < ids[3] + 1:
					net._otherId = ids[3] + 1
				if net._pageId < int(page._id[1:]) + 1:
					net._pageId = int(page._id[1:]) + 1
				if indice == "main":
					net._tab.blockSignals(True)
					net._tab.addTab(page, page.name())
					net._tab.blockSignals(False)
				for indice2, page2 in aux.items():
					elem = page2.getElementById(indice)
					if elem is not None:
						page._subRef = elem
						elem.setSubPage(page)
						page.setName("Ref_" + elem._id)
						break
			net._page = aux["main"]
			net._pages = [aux["main"]]
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
		
	def newNet(id, window):
		ans = PFSNet(id, window)
		page = PFSPage.newPage(ans.requestId(PFSPage), window._sm, ans)
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
			page._subRef = element
			openac = PFSOpenActivity(self.requestId(PFSOpenActivity), 20, 10, 100)
			self.addItemNoUndo(openac, page)
			closeac = PFSCloseActivity(self.requestId(PFSCloseActivity), page._scene.sceneRect().width()-20, 10, 100)
			self.addItemNoUndo(closeac, page)
			self._idPage = self._idPage + 1
			self._sm.fixTransitions(page._scene)
			return page
		return None
		
	def deleteElements(self):
		if len(self._pages) == 0:
			return
		scene = self._tab.currentWidget()._scene
		itemsSeleted = scene.selectedItems()
		if len(itemsSeleted) == 0:
			if self._tab.currentWidget() == self._page:
				return
			x = PFSUndoDeletePage(self._tab.currentWidget())
			self.undoStack.push(x)
			return
		itemsDeleted = []
		for item in itemsSeleted:
			if not item.canDelete():
				continue
			if isinstance(item, PFSNode):
				item.deleted.emit()
			itemsDeleted.append(item)
		if len(itemsDeleted) > 0:
			x = PFSUndoDelete(itemsDeleted)
			self.undoStack.push(x)
	
	def pasteElements(self, elements):
		self._pasteList = elements
	
	def pasteItems(self, pos):
		ans = []
		aux = {}
		for elem in self._pasteList:
			if isinstance(elem, PFSRelationContent):
				continue
			oldId = elem._id
			id = self.requestId(elem)
			if isinstance(elem, PFSActivityContent):
				e = PFSActivity.paste(elem, id, pos.x(), pos.y())
				ans.append(e)
				aux[oldId] = e
			elif isinstance(elem, PFSDistributorContent):
				e = PFSDistributor.paste(elem, id, pos.x(), pos.y())
				ans.append(e)
				aux[oldId] = e
		for elem in self._pasteList:
			if not isinstance(elem, PFSRelationContent):
				continue
			oldId = elem._id
			id = self.requestId(elem)
			e = PFSRelation.paste(elem, id, pos.x(), pos.y(), aux)
			ans.append(e)
		x = PFSUndoAdd(ans, self._tab.currentWidget()._scene)
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
		if element == PFSActivity or isinstance(element, PFSActivityContent):
			ans = "A" + str(self._activityId)
			self._activityId = self._activityId + 1
		elif element == PFSDistributor or isinstance(element, PFSDistributorContent):
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
	
	def changeTab(self, index: int):
		self._prop.clear()
		self._tree.clear()
		self.tree()		
		if index < 0:
			return
		self._tab.widget(index)._scene.clearSelection()
		self._window._main.tabChanged.emit()
	
	def fillProperties(self, props):
		if len(props) > 0:
			self._prop.setRowCount(0)
			self._prop.setRowCount(len(props))
			i = 0
			for line in props:
				if isinstance(line[0], QTableWidgetItem):
					self._prop.setItem(i, 0, line[0])
				else:
					self._prop.setCellWidget(i, 0, line[0])
				if isinstance(line[1], QTableWidgetItem):
					self._prop.setItem(i, 1, line[1])
				else:
					self._prop.setCellWidget(i, 1, line[1])
				if isinstance(line[0], PFSTableLabelTags):
					self._prop.setRowHeight(i, 100)
				i = i + 1
				
	def closeTab(self, ind):
		w = self._tab.widget(ind)
		self._pages.remove(w)
		self._tab.removeTab(ind)