from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget
from PyQt5.QtWidgets import QTableWidgetItem, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtGui import QMouseEvent, QTransform, QKeyEvent, QPainter
from element import PFSActivity, PFSDistributor, PFSRelation
from statemachine import PFSStateMachine
from extra import PFSTextBox
from undo import *

class PFSScene(QGraphicsScene):
	DELTA = 20.0
	inserted = pyqtSignal()
	edited = pyqtSignal()
	shiftInserted = pyqtSignal()
	def __init__(self, w: int, h: int, parentState: PFSStateMachine, page):
		super(QGraphicsScene, self).__init__()
		self._backgroundPoints = []
		self.resize(w,h)
		self._paintGrid = False
		self._parentState = parentState
		self._page = page
		self._tempSource = None
		self._tempActivity = None
		self._lastPos = QPoint(0,0)
		self._lastItemClicked = None
		self._wasMoving = False
		
	def setPaintGrid(self, v: bool= True):
		self._paintGrid = v
		self.update()
		
	def resize(self, w: int, h: int, l: int= 0, t: int= 0):
		self.setSceneRect(l, t, w, h)
		sx = int(w/self.DELTA - 1)
		sy = int(h/self.DELTA - 1)
		self._backgroundPoints = [QPoint((i+0.5)*self.DELTA, (j+0.5)*self.DELTA) for i in range(sx) for j in range(sy)]
		self.update()
		
	def mouseReleaseEvent(self, ev: QGraphicsSceneMouseEvent):
		if self._parentState._sNormal and not self._wasMoving:
			it = self.itemAt(ev.scenePos(), QTransform())
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.clearSelection()
			if it is not None:
				it.setSelected(True)
			itList = self.selectedItems()
			if len(itList) == 1:
				self._page._net.fillProperties(itList[0].propertiesTable())
			if len(itList) == 0:
				self._page._net.fillProperties(self._page.propertiesTable())
			self.update()
		self._wasMoving = False
		QGraphicsScene.mouseReleaseEvent(self, ev)
		
	def mousePressEvent(self, ev: QGraphicsSceneMouseEvent):
		if ev.button() == Qt.RightButton:
			self._page._net._window._main.tabChanged.emit()
			return
		self._lastPos = ev.scenePos()
		self._lastItemClicked = self.itemAt(ev.scenePos(), QTransform())
		if self._parentState._sPasting:
			self._page._net.pasteItems(self._lastPos)
			self.inserted.emit()
		if self._parentState._sDistributor:
			pos = ev.scenePos()
			elem = PFSDistributor(self._page._net.requestId(PFSDistributor), pos.x(), pos.y())
			self._page._net.addItem(elem, self._page)
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			return
		if self._parentState._sActivity:
			pos = ev.scenePos()
			elem = PFSActivity(self._page._net.requestId(PFSActivity), pos.x(), pos.y(), "Activity")
			self._page._net.addItem(elem, self._page)
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
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
				elem = PFSRelation.createRelation(self._page._net.requestId(PFSRelation), self._tempSource, it)
				if elem is not None:
					self._page._net.addItem(elem, self._page)
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			else:
				self.shiftInserted.emit()
			self._tempSource = None
			return
		if self._parentState._sNormal:
			self._page._net._prop.clear()
			it = self._lastItemClicked
			return
		if self._parentState._sTiping:
			it = self._lastItemClicked
			if it is None or not isinstance(it, QGraphicsProxyWidget):
				if self._tempActivity is not None:
					x = PFSUndoSetText(self._tempActivity, self._line.widget().toPlainText(), self)
					self._page._net.undoStack.push(x)					
				self.removeItem(self._line)
				self.inserted.emit()
			QGraphicsScene.mousePressEvent(self, ev)
			return
		QGraphicsScene.mousePressEvent(self, ev)
	
	def keyPressEvent(self, ev:QKeyEvent):
		if self._parentState._sTiping:
			QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Escape:
			self._page._net._window._main.tabChanged.emit()
			return
		if ev.key() == Qt.Key_Up:
			itList = self.selectedItems()
			if len(itList) > 0:
				x = PFSUndoKeyMove(itList, 0, -10)
				self._page._net.undoStack.push(x)
			else:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Down:
			itList = self.selectedItems()
			if len(itList) > 0:
				x = PFSUndoKeyMove(itList, 0, 10)
				self._page._net.undoStack.push(x)
			else:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Left:
			itList = self.selectedItems()
			if len(itList) > 0:
				x = PFSUndoKeyMove(itList, -10, 0)
				self._page._net.undoStack.push(x)
			else:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		if ev.key() == Qt.Key_Right:
			itList = self.selectedItems()
			if len(itList) > 0:
				x = PFSUndoKeyMove(itList, 10, 0)
				self._page._net.undoStack.push(x)
			else:
				QGraphicsScene.keyPressEvent(self, ev)
			return
		QGraphicsScene.keyPressEvent(self, ev)
		
	def mouseDoubleClickEvent(self, ev):
		pos = ev.scenePos()
		it = self.itemAt(pos, QTransform())
		if isinstance(it, PFSActivity):
			if not it.hasSubPage():
				self._page._net.createPage(it)
			self._page._net.openPage(it)
	
	def mouseMoveEvent(self, ev: QGraphicsSceneMouseEvent):
		if ev.buttons() == Qt.NoButton:
			return
		pos = ev.scenePos()
		if self._lastItemClicked is None or not self._lastItemClicked.isSelected():
			return
		itList = self.selectedItems()
		if len(itList) > 0:
			self._wasMoving = True
			pos = ev.scenePos()
			x = pos.x() - self._lastPos.x()
			y = pos.y() - self._lastPos.y()
			x = PFSUndoMouseMove(itList, x, y)
			self._page._net.undoStack.push(x)
			self._lastPos = pos
			self.update()
		
	def drawBackground(self, p: QPainter, r: QRect):
		p.drawRect(self.sceneRect())
		if not self._paintGrid:
			return
		p.setPen(Qt.SolidLine)
		for point in self._backgroundPoints:
			p.drawPoint(point)

class PFSView(QGraphicsView):
	def __init__(self, scene: PFSScene):
		super(QGraphicsView, self).__init__(scene)