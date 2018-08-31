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
		self._paintGrid = True
		self._parentState = parentState
		self._page = page
		self._tempSource = None
		self._tempActivity = None
		self._lastPos = QPoint(0,0)
		self._lastItemClicked = None
		
	def getNewDistributorId(self) -> str:
		ans = "D" + str(self._page._net._distributorId)
		self._page._net._distributorId = self._page._net._distributorId + 1
		return ans
	
	def getNewActivityId(self) -> str:
		ans = "A" + str(self._page._net._activityId)
		self._page._net._activityId = self._page._net._activityId + 1
		return ans
	
	def getNewRelationId(self) -> str:
		ans = "R" + str(self._page._net._relationId)
		self._page._net._relationId = self._page._net._relationId + 1
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
			elem = PFSDistributor(self.getNewDistributorId(), pos.x(), pos.y())
			x = PFSUndoAdd([elem], self)
			self._page._net.undoStack.push(x)
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			return
		if self._parentState._sActivity:
			pos = ev.scenePos()
			elem = PFSActivity(self.getNewActivityId(), pos.x(), pos.y(), "Activity")
			x = PFSUndoAdd([elem], self)
			self._page._net.undoStack.push(x)
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
				elem = PFSRelation.createRelation(self.getNewRelationId(), self._tempSource, it)
				if elem is not None:
					x = PFSUndoAdd([elem], self)
					self._page._net.undoStack.push(x)				
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.inserted.emit()
			else:
				self.shiftInserted.emit()
			self._tempSource = None
			return
		if self._parentState._sNormal:
			self._page._net._prop.clear()
			it = self._lastItemClicked
			if int(ev.modifiers()) & Qt.ShiftModifier == 0:
				self.clearSelection()
				QGraphicsScene.mousePressEvent(self, ev)
			if it is not None:
				it.setSelected(True)
			itList = self.selectedItems()
			if len(itList) == 1:
				i = 0
				for line in itList[0].propertiesTable():
					self._page._net._prop.setItem(i, 0, line[0])
					self._page._net._prop.setItem(i, 1, line[1])
					i = i + 1
			if len(itList) == 0:
				i = 0
				for line in self._page.propertiesTable():
					self._page._net._prop.setItem(i, 0, line[0])
					self._page._net._prop.setItem(i, 1, line[1])
					i = i + 1
			self.update()
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
		if len(itList) > 0:
			pos = ev.scenePos()
			x = pos.x() - self._lastPos.x()
			y = pos.y() - self._lastPos.y()
			x = PFSUndoMouseMove(itList, x, y)
			self._page._net.undoStack.push(x)
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