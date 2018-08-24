from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QTabWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect, QPoint, QXmlStreamWriter, QXmlStreamReader
from PyQt5.QtGui import QMouseEvent, QPainter
from element import PFSActivity, PFSDistributor
from xml import PFSXmlBase
from statemachine import PFSStateMachine

class PFSScene(QGraphicsScene):
	DELTA = 20.0
	inserted = pyqtSignal()
	def __init__(self, w: int, h: int, parentState: PFSStateMachine, net):
		super(QGraphicsScene, self).__init__()
		self._backgroundPoints: [QPoint] = []
		self.resize(w,h)
		self._paintGrid = True
		self._parentState = parentState
		self._net = net
		
	def getNewDistributorId(self) -> str:
		ans = "D" + str(self._net._distributorId)
		self._net._distributorId = self._net._distributorId + 1
		return ans
	
	def getNewActivityId(self) -> str:
		ans = "A" + str(self._net._activityId)
		self._net._activityId = self._net._activityId + 1
		return ans	
		
	def setPaintGrid(self, v: bool= True):
		self._paintGrid = v
		self.update()
		
	def resize(self, w: int, h: int):
		self.setSceneRect(0, 0, w, h)
		sx = int(w/self.DELTA - 1)
		sy = int(h/self.DELTA - 1)
		self._backgroundPoints = [QPoint((i+0.5)*self.DELTA, (j+0.5)*self.DELTA) for i in range(sx) for j in range(sy)]
		self.update()
		
	def mousePressEvent(self, ev: QMouseEvent):
		if self._parentState._sDistributor:
			pos = ev.scenePos()
			self.addItem(PFSDistributor(self.getNewDistributorId(), pos.x(), pos.y()))
			self.inserted.emit()
			self._net.setSaved(False)
		if self._parentState._sActivity:
			pos = ev.scenePos()
			self.addItem(PFSActivity(self.getNewActivityId(), pos.x(), pos.y(), "Activity"))
			self.inserted.emit()
			self._net.setSaved(False)
	
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
			if isinstance(e, PFSActivity) or isinstance(e, PFSDistributor):
				e.generateXml(xml)
		xml.writeEndElement() #fim da page
		
	def resizeScene(self):
		self._scene.resize(int(self.txtWidth.text()), int(self.txtHeight.text()))
	
	def getTabName(self) -> str:
		if self._file is None:
			return "New_Model"
		return "New_Model"
	
	def newPage(id: str, sm: PFSStateMachine, net):
		return PFSPage(id, 4000, 4000, sm, net)
		
	def createFromXml(xml: QXmlStreamReader, sm: PFSStateMachine, net):
		success = True
		if PFSXmlBase.nextTool(xml) and xml.name() == "pagetype":
			if not xml.attributes().hasAttribute("id"):
				success = False			
			id = xml.attributes().value("id")
			
			xml.readNextStartElement()
			pos = PFSXmlBase.getPosition(xml)
			if pos is None:
				h = 4000
				w = 4000
			else:
				w = pos.x
				h = pos.y
			page = PFSPage(id, w, h, sm, net)
			if PFSXmlBase.nextTool(xml):
				if xml.name() == "activity":
					ac = PFSActivity.createFromXml(xml)
					if ac is not None:
						page._scene.addItem(ac)
				if xml.name() == "distributor":
					di = PFSDistributor.createFromXml(xml)
					if di is not None:
						page._scene.addItem(di)
		if success:
			return page
		return None

class PFSNet(QWidget):
	changed = pyqtSignal()
	def __init__(self, id: str, sm: PFSStateMachine):
		super(QWidget, self).__init__()
		self._filename: str = None
		self._filepath: str = None
		self._id = id
		self._layout = QHBoxLayout()
		self._tab = QTabWidget()
		self.setLayout(self._layout)
		self._pages: [PFSPage] = []
		self._idPage = 0
		self._sm = sm
		self._saved = True
		self._distributorId = 0
		self._activityId = 0
		self._relationId = 0		
		
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
		
	def createFromXml(xml: QXmlStreamReader, sm: PFSStateMachine):
		xml.readNextStartElement()
		if xml.name() != "PetriNetDoc":
			return None
		xml.readNextStartElement()
		nets = []
		while xml.name() == "net":
			success = True
			xml.readNextStartElement()
			id = xml.attributes().value("id")
			if id == None:
				success = False
			net = PFSNet(id, sm)
			xml.readNextStartElement()
			while xml.name() != "page":
				xml.readNextStartElement()
			pages = []
			while xml.name() == "page":
				page = PFSPage.createFromXml(xml, sm, net)
				if page is None and len(pages) == 0:
					success = False
				if page is not None:
					pages.append(page)
			if len(pages) > 0 and succes:
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