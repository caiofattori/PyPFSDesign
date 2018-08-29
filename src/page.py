from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QTabWidget, QPushButton, QGraphicsProxyWidget, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect, QPoint, QXmlStreamWriter, QXmlStreamReader
from PyQt5.QtGui import QMouseEvent, QPainter, QTransform, QKeyEvent, QKeySequence
from PyQt5.QtXml import QDomDocument, QDomNode
from element import PFSActivity, PFSDistributor, PFSRelation
from xml import PFSXmlBase
from statemachine import PFSStateMachine
from extra import PFSTextBox

class PFSScene(QGraphicsScene):
	DELTA = 20.0
	inserted = pyqtSignal()
	edited = pyqtSignal()
	shiftInserted = pyqtSignal()
	def __init__(self, w: int, h: int, parentState: PFSStateMachine, net):
		super(QGraphicsScene, self).__init__()
		self._backgroundPoints = []
		self.resize(w,h)
		self._paintGrid = True
		self._parentState = parentState
		self._net = net
		self._tempSource = None
		self._tempActivity = None
		self._lastPos = QPoint(0,0)
		self._lastItemClicked = None
		
	def getNewDistributorId(self) -> str:
		ans = "D" + str(self._net._distributorId)
		self._net._distributorId = self._net._distributorId + 1
		return ans
	
	def getNewActivityId(self) -> str:
		ans = "A" + str(self._net._activityId)
		self._net._activityId = self._net._activityId + 1
		return ans
	
	def getNewRelationId(self) -> str:
		ans = "R" + str(self._net._relationId)
		self._net._relationId = self._net._relationId + 1
		return ans
		
	def setPaintGrid(self, v: bool= True):
		self._paintGrid = v
		self.update()
		
	def resize(self, w: int, h: int, l: int= 0, t: int= 0):
		self.setSceneRect(l, t, w, h)
		sx = int(w/self.DELTA - 1)
		sy = int(h/self.DELTA - 1)
		self._backgroundPoints = [QPoint((i+0.5)*self.DELTA, (j+0.5)*self.DELTA) for i in range(sx) for j in range(sy)]
		self.update()
		
	def mousePressEvent(self, ev: QGraphicsSceneMouseEvent):
		self._lastPos = ev.scenePos()
		self._lastItemClicked = self.itemAt(ev.scenePos(), QTransform())
		if self._parentState._sDistributor:
			pos = ev.scenePos()
			self.addItem(PFSDistributor(self.getNewDistributorId(), pos.x(), pos.y()))
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			self._net.setSaved(False)
			return
		if self._parentState._sActivity:
			print("aqui1")
			pos = ev.scenePos()
			self.addItem(PFSActivity(self.getNewActivityId(), pos.x(), pos.y(), "Activity"))
			print("aqui2")
			x = int(ev.modifiers())
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			self._net.setSaved(False)
			return
		if self._parentState._sRelationS:
			it = self._lastItemClicked
			if it is not None:
				self._tempSource = it
				self.inserted.emit()
			return
		if self._parentState._sRelationT:
			it = self._lastItemClicked
			if it is not None:
				rel = PFSRelation.createRelation(self.getNewRelationId(), self._tempSource, it)
				self.addItem(rel)
				self._net.setSaved(False)
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			else:
				self.shiftInserted.emit()
			self._tempSource = None
			return
		if self._parentState._sNormal:
			it = self._lastItemClicked
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.clearSelection()
				QGraphicsScene.mousePressEvent(self, ev)
			if it is not None:
				it.setSelected(True)
			self.update()
			return
		if self._parentState._sTiping:
			it = self._lastItemClicked
			if it is None or not isinstance(it, QGraphicsProxyWidget):
				if self._tempActivity is not None:
					self._tempActivity.setText(self._line.widget().toPlainText())
				self.removeItem(self._line)
				self.inserted.emit()
			QGraphicsScene.mousePressEvent(self, ev)
			return
		QGraphicsScene.mousePressEvent(self, ev)
	
	def keyPressEvent(self, ev:QKeyEvent):
		if self._parentState._sTiping:
			QGraphicsScene.keyPressEvent(self, ev)
			return
		'''if ev.key() == Qt.Key_Delete:
			itList = self.selectedItems()
			for item in itList:
				self.removeItem(item)
			self.update()
			return'''
		if ev.key() == Qt.Key_Up:
			itList = self.selectedItems()
			for item in itList:
				item.move(0,-10)
			self.update()
			if len(itList) == 0:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Down:
			itList = self.selectedItems()
			for item in itList:
				item.move(0,10)
			self.update()
			if len(itList) == 0:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Left:
			itList = self.selectedItems()
			for item in itList:
				item.move(-10,0)
			self.update()
			if len(itList) == 0:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Right:
			itList = self.selectedItems()
			for item in itList:
				item.move(10,0)
			self.update()
			if len(itList) == 0:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		QGraphicsScene.keyPressEvent(self, ev)
	
	def mouseDoubleClickEvent(self, ev):
		if self._parentState._sNormal:
			pos = ev.scenePos()
			it = self.itemAt(pos, QTransform())
			if isinstance(it, PFSActivity):
				self.edited.emit()
				self._line = PFSTextBox(self, it)
				self._tempActivity = it
				self.addItem(self._line)
				self._line.setGeometry(it.sceneBoundingRect())
				self.setFocusItem(self._line)
		QGraphicsScene.mouseDoubleClickEvent(self, ev)
	
	def mouseMoveEvent(self, ev: QGraphicsSceneMouseEvent):
		if ev.buttons() == Qt.NoButton:
			return
		pos = ev.scenePos()
		if self._lastItemClicked is None or not self._lastItemClicked.isSelected():
			return
		itList = self.selectedItems()
		pos = ev.scenePos()
		x = pos.x() - self._lastPos.x()
		y = pos.y() - self._lastPos.y()
		for item in itList:
			item.move(x, y)
		self._lastPos = pos
		self.update()
		
	def drawBackground(self, p: QPainter, r: QRect):
		if not self._paintGrid:
			return
		p.setPen(Qt.SolidLine)
		for point in self._backgroundPoints:
			p.drawPoint(point)

class PFSView(QGraphicsView):
	def __init__(self, scene: PFSScene):
		super(QGraphicsView, self).__init__(scene)

class PFSPage(QWidget):
	def __init__(self, id: str, w: int, h: int, stateMachine: PFSStateMachine, net):
		super(QWidget, self).__init__()
		self._id = id
		self._scene = PFSScene(w, h, stateMachine, net)
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
		self._net = net
		
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
			self._scene.resize(r-l, b-t, l, t)
			self._net.setSaved(False)
			self.txtWidth.setText(str(r-l))
			self.txtHeight.setText(str(b-t))
	
	def resizeScene(self):
		self._scene.resize(int(self.txtWidth.text()), int(self.txtHeight.text()))
		self._net.setSaved(False)
	
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
		self._pages = []
		self._idPage = 0
		self._sm = sm
		self._saved = True
		self._distributorId = 0
		self._activityId = 0
		self._relationId = 0
		#self.undoStack = QUndoStack(self)
		#self.undoAction = self.undoStack.createUndoAction(self, "Desfazer")
		#self.undoAction.setShortcuts(QKeySequence.Undo)
		
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
				nets.append(net)
		return nets	
		
	def isSaved(self) -> bool:
		return self._saved
	
	def getTabName(self) -> str:
		if self._filename is None:
			ans = "New model"
		else:
			ans = self._filename
		if self.isSaved():
			return ans
		return ans + "*"
		
	def newNet(id, sm: PFSStateMachine):
		ans = PFSNet(id, sm)
		page = PFSPage.newPage("pg" + str(ans._idPage), sm, ans)
		ans._idPage = ans._idPage + 1
		ans._pages.append(page)
		ans._layout.addWidget(page)
		return ans
	
	def setSaved(self, value: bool=True):
		self._saved = value
		self.changed.emit()
		
	def deleteElements(self):
		for item in self._pages[0]._scene.selectedItems():
			self._pages[0]._scene.removeItem(item)