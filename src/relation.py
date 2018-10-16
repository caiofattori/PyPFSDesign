from element import *
from generic import *
from PyQt5.QtCore import Qt, QPointF, QRect, QRectF, QXmlStreamWriter, QEvent, QLineF
from tree import PFSTreeItem
from image import PFSRelationIcon
from contents import PFSRelationContent, PFSSecondaryFlowContent
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QIcon, QPainterPath, QPolygon, QPolygonF, QColor, QPainterPathStroker
from xml import *
from PyQt5.QtXml import QDomNode
from table import *
from undo import *
from polygon import PFSPolygon

class PFSRelationPoint(QGraphicsRectItem):
	def __init__(self, parent, x, y):
		QGraphicsRectItem.__init__(self, x, y, 6, 6, parent)
		self.setFlag(QGraphicsItem.ItemIsSelectable)
	
	def move(self, x, y):
		self.moveBy(x, y)
		self.parentItem().updatePoints()
		#self.changed.emit()
	
	def idItem(self):
		return self.parentItem().idItem()
	
	def propertiesTable(self):
		return self.parentItem().propertiesTable()
	
	def paint(self, p, o, m):
		if self.parentItem().isSelected() or self.scene()._parentState._sEditPoint:
			if self.scene()._parentState._sEditPoint:
				if self.isSelected():
					p.setPen(Qt.black)
				else:
					p.setPen(Qt.red)
				p.setBrush(QBrush(Qt.red, Qt.SolidPattern))
			else:
				p.setPen(Qt.black)
				p.setBrush(QBrush(Qt.black, Qt.SolidPattern))
			r = self.rect()
			r.moveCenter(r.center() - QPointF(3, 3))
			p.drawRect(r)

class PFSRelation(PFSElement):
	def __init__(self, id: str, source: PFSNode, target: PFSNode):
		PFSElement.__init__(self,id)
		self._source = source
		self._sourceNum = 0
		self._target = target
		self._targetNum = 0
		self._midPoints = []
		self._firstPoint = None
		self._lastPoint = None
		self._pen = QPen(Qt.black)
		self._penSelected = QPen(PFSElement.SELECTED_PEN)
		self._penSelectedAlt = QPen(PFSElement.SELECTED_PEN_ALT)
		self._obj = PFSGraphItems()
		self.penEdited = self._obj.penEdited
		self._stroke = QPainterPathStroker()
		self._stroke.setWidth(20)
	
	def sceneEventFilter(self, item, ev:QEvent):
		print(ev.type())
		return QGraphicsItem.sceneEventFilter(self, item, ev)
	
	def closestMiddlePoint(self, pos:QPointF):
		d = -1
		p1 = None
		for p in self._midPoints:
			aux = QLineF(pos, p.sceneBoundingRect().topLeft()).length()
			if p1 is None or aux < d:
				p1 = p
				d = aux
		return p1
	
	def closeMiddlePoint(self, pos:QPointF):
		for p in self._midPoints:
			if QLineF(pos, p.sceneBoundingRect().topLeft()).length() < 3:
				return p
		return None
	
	def closestPoint(self, pos:QPointF):
		d = -1
		p = None
		p1 = self._firstPoint
		prev = -1
		for i in range(len(self._midPoints)):
			p2 = self._midPoints[i].sceneBoundingRect().topLeft()
			l = QLineF(p1, p2)
			x = QPointF.dotProduct(pos-p1, p2-p1)/l.length()
			if x < 0:
				paux = p1
			elif x > 1:
				paux = p2
			else:
				paux = l.pointAt(x)
			aux = QLineF(paux, pos).length()
			if p is None or aux < d:
				p = paux
				d = aux
				prev = i
			p1 = p2
		p2 = self._lastPoint
		l = QLineF(p1, p2)
		x = QPointF.dotProduct(pos-p1, p2-p1)/(l.length()*l.length())
		if x < 0:
			paux = p1
		elif x > 1:
			paux = p2
		else:
			paux = l.pointAt(x)
		aux = QLineF(paux, pos).length()
		if p is None or aux < d:
			p = paux
			d = aux
			prev = -1
		return p, prev
	
	def addMiddlePoint(self, point:QPointF, i=-1):
		p = PFSRelationPoint(self, point.x(), point.y())
		#self.installSceneEventFilter(p)
		if i < 0:
			self._midPoints.append(p)
		else:
			self._midPoints.insert(i, p)
	
	def createMiddlePoint(self, pos:QPointF):
		p, i = self.closestPoint(pos)
		self.addMiddlePoint(p, i)
		self.scene().update()
	
	def moveX(self, txt, update=True):
		value = float(txt)
		for point in self._midPoints:
			point.moveBy(value, 0)
		if update:
			self.scene().update()
			
	def moveY(self, txt, update=True):
		value = float(txt)
		for point in self._midPoints:
			point.moveBy(0, value)
		if update:
			self.scene().update()	
	
	def simpleTree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSRelationIcon()))
		tree.clicked.connect(self.selectSingle)
		return tree
	
	def tree(self, parent):
		tree = PFSTreeItem(parent, [self._id], 0, QIcon(PFSRelationIcon()))
		tree.clicked.connect(self.selectSingle)
		child = self._source.simpleTree(tree)
		child = self._target.simpleTree(tree)
		return tree
	
	def hasSubPage(self):
		return False
	
	def copy(self, x, y):
		ans = PFSRelationContent()
		ans._id = self._id
		ans._midPoints = []
		for point in ans._midPoints:
			ans._midPoints.append(QPointF(point.sceneBoundingRect().topLeft().x()-x, point.sceneBoundingRect().topLeft().y()-y))
		ans._pen = self._pen
		ans._tags = self._tags
		ans._source = self._source._id
		ans._target = self._target._id
		ans._sourceNum = self._sourceNum
		ans._targetNum = self._targetNum
		return ans
	
	def paste(content, id, dx, dy, itemList):
		ans = PFSRelation.createRelation(id, itemList[content._source], itemList[content._target])
		ans._pen = content._pen
		ans._sourceNum = content._sourceNum
		ans._targetNum = content._targetNum
		for tag in content._tags:
			ans.addTag(tag._name, tag._use, False)
		for point in content._midPoints:
			ans._midPoints.append(PFSRelationPoint(ans, point.x()+dx, point.y()+dy))
		ans.updatePoints()
		return ans
	
	def createRelation(id: str, source: PFSNode, target: PFSNode):
		if isinstance(source, PFSActive):
			if isinstance(target, PFSPassive):
				r = PFSRelation(id, source, target)
				source.changed.connect(r.updatePoints)
				target.changed.connect(r.updatePoints)
				source.deleted.connect(r.putInDelete)
				target.deleted.connect(r.putInDelete)
				return r
		elif isinstance(source, PFSPassive):
			if isinstance(target, PFSActive):
				r = PFSRelation(id, source, target)
				source.changed.connect(r.updatePoints)
				target.changed.connect(r.updatePoints)
				source.deleted.connect(r.putInDelete)
				target.deleted.connect(r.putInDelete)
				return r
		return None
	
	def updatePoints(self):
		if len(self._midPoints) == 0:
			if isinstance(self._source, PFSActive):
				self._firstPoint = self._source.getBestRelationPointOutput(QRect(self._target.x(), self._target.y(), self._target._width, self._target._height).center(), self._sourceNum)
				self._lastPoint = self._target.getBestRelationPointInput(self._firstPoint, self._targetNum)
			else:
				self._lastPoint = self._target.getBestRelationPointInput(QRect(self._source.x(), self._source.y(), self._source._width, self._source._height).center(), self._targetNum)
				self._firstPoint = self._source.getBestRelationPointOutput(self._lastPoint, self._sourceNum)
		else:
			self._firstPoint = self._source.getBestRelationPointOutput(self._midPoints[0].sceneBoundingRect().topLeft(), self._sourceNum)
			self._lastPoint = self._target.getBestRelationPointInput(self._midPoints[-1].sceneBoundingRect().topLeft(), self._targetNum)
	
	def getPath(self) -> QPainterPath:
		pol = QPolygonF()
		pol.append(self._firstPoint)
		for p in self._midPoints:
			pol.append(p.sceneBoundingRect().topLeft())
		pol.append(self._lastPoint)
		ans = QPainterPath()
		ans.addPolygon(pol)
		return ans
	
	def shape(self) -> QPainterPath:
		return self._stroke.createStroke(self.getPath())
	
	def paint(self, p: QPainter, o: QStyleOptionGraphicsItem, w: QWidget):
		p.setPen(self._pen)
		if self.isSelected():
			if self._pen.color() == PFSElement.SELECTED_PEN:
				p.setPen(self._penSelectedAlt)
			else:
				p.setPen(self._penSelected)
		path = self.getPath()
		p.drawPath(path)
		if len(self._midPoints) == 0:
			ang = math.atan2(self._lastPoint.y()-self._firstPoint.y(), self._lastPoint.x()-self._firstPoint.x())
		else:
			ang = math.atan2(self._lastPoint.y()-self._midPoints[-1].sceneBoundingRect().topLeft().y(), self._lastPoint.x()-self._midPoints[-1].sceneBoundingRect().topLeft().x())
		p.save()
		p.translate(self._lastPoint)
		p.rotate(ang*180/math.pi)
		self.drawArrow(p)
		p.restore()
	
	def drawArrow(self, p:QPainter):
		p.drawLine(-10, -6, 0, 0)
		p.drawLine(-10, 6, 0, 0)
	
	def boundingRect(self):
		if self._firstPoint is None or self._lastPoint is None:
			self.updatePoints()
		t = min(self._firstPoint.y(),self._lastPoint.y())
		b = max(self._firstPoint.y(),self._lastPoint.y())
		l = min(self._firstPoint.x(),self._lastPoint.x())
		r = max(self._firstPoint.x(),self._lastPoint.x())
		for po in self._midPoints:
			p = po.sceneBoundingRect().topLeft()
			if p.x() < l:
				l = p.x()
			if p.x() > r:
				r = p.x()
			if p.y() < t:
				t = p.y()
			if p.y() > b:
				b = p.y()
		w = r-l
		if w < 5:
			w = 5
		h = b-t
		if h < 5:
			h = 5
		return QRectF(l, t, w, h)
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("relation")
		xml.writeAttribute("id", self._id)
		xml.writeAttribute("source", self._source._id)
		xml.writeAttribute("sourceport", str(self._sourceNum))
		xml.writeAttribute("target", self._target._id)
		xml.writeAttribute("targetport", str(self._targetNum))
		points = [p.sceneBoundingRect().topLeft() for p in self._midPoints]
		PFSXmlBase.graphicsArc(xml, points, self._pen)
		PFSBasicElement.generateXml(self, xml)
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)
		
	def move(self, x, y):
		delta = QPointF(x, y)
		for p in self._midPoints:
			p.prepareGeometryChange()
			p.moveBy(x, y)
		#self.scene().update()
	
	def createFromXml(node: QDomNode):
		if node.nodeName() != "relation":
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("id")):
			return None
		id = attr.namedItem("id").nodeValue()
		if not (attr.contains("source") and attr.contains("target")):
			return None
		source = attr.namedItem("source").nodeValue()
		target = attr.namedItem("target").nodeValue()
		sourceNum = 0
		targetNum = 0
		if attr.contains("sourceport"):
			sourceNum = int(attr.namedItem("sourceport").nodeValue())
		if attr.contains("targetport"):
			targetNum = int(attr.namedItem("targetport").nodeValue())
		graphics = None
		tags = []
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getArc(child)
			if child.nodeName() == "tags":
				tags = PFSBasicElement.createFromXml(child)
		re = PFSRelationContent()
		re._id = id
		re._source = source
		re._sourceNum = sourceNum
		re._target = target
		re._targetNum = targetNum
		if graphics is not None and graphics.line is not None:
			re._pen = graphics.line
		re._midPoints = []
		if graphics is not None and graphics.pos is not None:
			for pos in graphics.pos:
				re._midPoints.append(QPointF(pos.x + 0.5, pos.y + 0.5))
		re._tags = tags
		return re
		
	def putInDelete(self):
		if self.scene() is not None:
			lst = self.scene()._itemsDeleted
			if self not in lst:
				lst.append(self)
	
	def setPenColor(self, color: QColor):
		self._pen.setColor(color)
		self.scene().update()
		
	def setPenStyle(self, style: Qt):
		self._pen.setStyle(style)
		self.scene().update()
		self.penEdited.emit(style)
		
	def setPenWidth(self, width: str):
		self._pen.setWidth(float(width))
		self.scene().update()
		
	def setSourceNum(self, text: str):
		self._sourceNum = int(text)
		if self.scene() is not None:
			self.updatePoints()
			self.scene().update()
			
	def setTargetNum(self, text: str):
		self._targetNum = int(text)
		if self.scene() is not None:
			self.updatePoints()
			self.scene().update()	
	
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Arco")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do contorno")
		lblValue = PFSTableValueButton(self._pen.color().name())
		lblValue.clicked.connect(self.changeLineColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Linha do contorno")
		lblValue = PFSTableValueCombo(self.PEN_LIST, self._pen.style())
		self.penEdited.connect(lblValue.updateText)
		lblValue.currentTextChanged.connect(self.changeLineStyle)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Espessura do contorno")
		lblValue = PFSTableValueText(str(self._pen.width()))
		lblValue.edited.connect(self.changeLineWidth)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Porta origem")
		lblValue = PFSTableValueCombo({str(x+1):str(x) for x in range(self._source.outputNum())}, str(self._sourceNum))
		lblValue.currentTextChanged.connect(self.changeSourceNum)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Porta destino")
		lblValue = PFSTableValueCombo({str(x+1):str(x) for x in range(self._target.inputNum())}, str(self._targetNum))
		lblValue.currentTextChanged.connect(self.changeTargetNum)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabelTags("Tags")
		lblValue = PFSTableValueBox(self._tags, self.createTag)
		ans.append([lblType, lblValue])		
		return ans
	
	def changeLineColor(self):
		color = QColorDialog.getColor(self._pen.color(), self.scene()._page._net, "Escolha a cor do contorno")
		if color.isValid() and color != self._pen.color():
			x = PFSUndoPropertyButton(color, self._pen.color(), self.setPenColor)
			x.setText("Alterar cor")
			self.scene()._page._net.undoStack.push(x)
			
	def changeLineStyle(self, text):
		if text in self.PEN_LIST:
			x = PFSUndoPropertyCombo(self.PEN_LIST[text], self._pen.style(), self.setPenStyle)
			x.setText("Alterar linha")
			self.scene()._page._net.undoStack.push(x)
	
	def changeLineWidth(self, prop):
		x = PFSUndoPropertyText(prop, self.setPenWidth)
		x.setText("Alterar espessura")
		self.scene()._page._net.undoStack.push(x)
		
	def changeSourceNum(self, text):
		try:
			x = PFSUndoPropertyCombo(str(int(text)-1), str(self._sourceNum), self.setSourceNum)
			x.setText("Alterar porta entrada")
			self.scene()._page._net.undoStack.push(x)
		except:
			pass
		
	def changeTargetNum(self, text):
		try:
			x = PFSUndoPropertyCombo(str(int(text)-1), str(self._targetNum), self.setTargetNum)
			x.setText("Alterar porta saída")
			self.scene()._page._net.undoStack.push(x)
		except:
			pass
		
class PFSSecondaryFlow(PFSRelation):
	def __init__(self, id, source, target):
		PFSRelation.__init__(self, id, source, target)
		self._pen = QPen(QBrush(Qt.black, Qt.SolidPattern), 5)
		self._penSelected = QPen(QBrush(PFSElement.SELECTED_PEN, Qt.SolidPattern), 5)
		self._penSelectedAlt = QPen(QBrush(PFSElement.SELECTED_PEN_ALT, Qt.SolidPattern), 5)
		self._lineX = 0
	
	def copy(self, x, y):
		ans = PFSSecondaryFlowContent()
		ans._id = self._id
		ans._midPoints = []
		for point in ans._midPoints:
			ans._midPoints.append(QPointF(point.sceneBoundingRect().topLeft().x()-x, point.sceneBoundingRect().topLeft().y()-y))
		ans._pen = self._pen
		ans._tags = self._tags
		ans._source = self._source._id
		ans._target = self._target._id
		ans._lineX = self._lineX
		return ans
	
	def paste(content, id, dx, dy, itemList):
		ans = PFSSecondaryFlow.createSecondaryFlow(id, itemList[content._source], itemList[content._target])
		ans._pen = content._pen
		ans._lineX = content._lineX
		for tag in content._tags:
			ans.addTag(tag._name, tag._use, False)
		for point in content._midPoints:
			ans._midPoints.append(PFSRelationPoint(ans, point.x()+dx, point.y()+dy))
		ans.updatePoints()
		return ans	
	
	def createSecondaryFlow(id: str, source: PFSNode, target: PFSNode):
		if isinstance(source, PFSActivity) and isinstance(target, PFSPassive):
			r = PFSSecondaryFlow(id, source, target)
			source.changed.connect(r.updatePoints)
			target.changed.connect(r.updatePoints)
			source.deleted.connect(r.putInDelete)
			target.deleted.connect(r.putInDelete)
			return r
		if isinstance(source, PFSPassive) and isinstance(target, PFSActivity):
			r = PFSSecondaryFlow(id, source, target)
			source.changed.connect(r.updatePoints)
			target.changed.connect(r.updatePoints)
			source.deleted.connect(r.putInDelete)
			target.deleted.connect(r.putInDelete)
			return r
		return None
	
	def generateXml(self, xml: QXmlStreamWriter):
		PFSXmlBase.open(xml)
		xml.writeStartElement("secondaryflow")
		xml.writeAttribute("id", self._id)
		xml.writeAttribute("source", self._source._id)
		xml.writeAttribute("target", self._target._id)
		xml.writeAttribute("linex", str(self._lineX))
		points = [p.sceneBoundingRect().topLeft() for p in self._midPoints]
		PFSXmlBase.graphicsArc(xml, points, self._pen)
		PFSBasicElement.generateXml(self, xml)
		xml.writeEndElement() #fecha distributor
		PFSXmlBase.close(xml)	
		
	def createFromXml(node: QDomNode):
		if node.nodeName() != "secondaryflow":
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("id")):
			return None
		id = attr.namedItem("id").nodeValue()
		if not (attr.contains("source") and attr.contains("target")):
			return None
		source = attr.namedItem("source").nodeValue()
		target = attr.namedItem("target").nodeValue()
		lineX = 0
		if attr.contains("linex"):
			lineX = float(attr.namedItem("linex").nodeValue())
		graphics = None
		tags = []
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getArc(child)
			if child.nodeName() == "tags":
				tags = PFSBasicElement.createFromXml(child)
		re = PFSSecondaryFlowContent()
		re._id = id
		re._source = source
		re._target = target
		re._lineX = lineX
		if graphics is not None and graphics.line is not None:
			re._pen = graphics.line
		if graphics is not None and graphics.pos is not None:
			re._midPoints = graphics.pos
		else:
			re._midPoints = []
		re._tags = tags
		return re
		
	def propertiesTable(self):
		ans = []
		lblType = PFSTableLabel("Elemento")
		lblValue = PFSTableNormal("Fluxo secundário")
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("ID")
		lblValue = PFSTableNormal(self._id)
		lblValue.setFlags(Qt.NoItemFlags)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Cor do contorno")
		lblValue = PFSTableValueButton(self._pen.color().name())
		lblValue.clicked.connect(self.changeLineColor)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Linha do contorno")
		lblValue = PFSTableValueCombo(self.PEN_LIST, self._pen.style())
		self.penEdited.connect(lblValue.updateText)
		lblValue.currentTextChanged.connect(self.changeLineStyle)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabel("Posição na atividade")
		lblValue = PFSTableValueText(str(self._lineX))
		lblValue.edited.connect(self.changeLineX)
		ans.append([lblType, lblValue])
		lblType = PFSTableLabelTags("Tags")
		lblValue = PFSTableValueBox(self._tags, self.createTag)
		ans.append([lblType, lblValue])
		return ans
	
	def changeLineX(self, prop):
		x = PFSUndoPropertyText(prop, self.setLineX)
		x.setText("Alterar posição do arco")
		self.scene()._page._net.undoStack.push(x)
	
	def setLineX(self, txt):
		self._lineX = float(txt)
		self.updatePoints()
		self.scene().update()
	
	def updatePoints(self):
		if len(self._midPoints) == 0:
			if isinstance(self._source, PFSActive):
				self._firstPoint = self._source.getBestRelationPointSecondary(QRect(self._target.x(), self._target.y(), self._target._width, self._target._height).center(), self._lineX)
				self._lastPoint = self._target.getBestRelationPointInput(self._firstPoint, 0)
			else:
				self._lastPoint = self._target.getBestRelationPointSecondary(QRect(self._source.x(), self._source.y(), self._source._width, self._source._height).center(), self._lineX)
				self._firstPoint = self._source.getBestRelationPointOutput(self._lastPoint, 0)
		else:
			self._firstPoint = self._source.getBestRelationPointOutput(self._midPoints[0].sceneBoundingRect().topLeft(), self._sourceNum)
			self._lastPoint = self._target.getBestRelationPointInput(self._midPoints[-1].sceneBoundingRect().topLeft(), self._targetNum)