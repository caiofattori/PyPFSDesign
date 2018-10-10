from PyQt5.QtGui import QFont, QGradient, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QRect, QXmlStreamReader, QXmlStreamWriter, QPoint
from PyQt5.QtXml import QDomNode

class PFSAux:
	def __init__(self):
		pass

class PFSXmlBase:
	STANDARDTEXTFONT = QFont("Helvetica", 12)
	def open(xml: QXmlStreamWriter):
		xml.writeStartElement("toolspecific")
		xml.writeAttribute("tool", "PFS")
		xml.writeAttribute("version", "1.0.0")
	
	def toolHasChild(node: QDomNode, value: str) -> bool:
		if node.nodeName() != "toolspecific":
			return False
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("tool") and attr.namedItem("tool").nodeValue() == "PFS"):
			return False
		if not (node.hasAttributes() and attr.contains("version") and attr.namedItem("version").nodeValue() == "1.0.0"):
			return False
		if not node.hasChildNodes():
			return False
		childs = node.childNodes()
		for i in range(childs.count()):
			if childs.at(i).nodeName() == value:
				return True
		return False
				
	def close(xml: QXmlStreamWriter):
		xml.writeEndElement()
		
	def position(xml: QXmlStreamWriter, x: int, y: int, tag: str="position"):
		xml.writeStartElement(tag)
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement() #fecha pos
	
	def getPosition(node: QDomNode):
		if node.nodeName() not in ["position", "dimension", "offset"]:
			return None
		if not (node.hasAttributes() and node.attributes().contains("x") and node.attributes().contains("y")):
			return None
		ans = PFSAux()
		ans.x = float(node.attributes().namedItem("x").nodeValue())
		ans.y = float(node.attributes().namedItem("y").nodeValue())
		return ans
		
	def font(xml: QXmlStreamWriter, font: QFont, align: str="left", rotation: int=0, tag: str="font"):
		xml.writeStartElement("font")
		xml.writeAttribute("family", font.family())
		if font.style() == QFont.StyleItalic:
			xml.writeAttribute("style", "italic")
		elif font.style() == QFont.StyleOblique:
			xml.writeAttribute("style", "oblique")
		else:
			xml.writeAttribute("style", "normal")
		xml.writeAttribute("size", str(font.pointSize()))
		v = ["bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900", "900"]
		if font.weight() <= 50:
			xml.writeAttribute("weight", "normal")
		else:
			xml.writeAttribute("weight", v[int((font.weight()-50)/4)])
		dec = []
		if font.underline():
			dec.append("underline")
		if font.overline():
			dec.append("overline")
		if font.strikeOut():
			dec.append("line-through")
		if len(dec) > 0:
			xml.writeAttribute("decoration", ";".join(dec))
		xml.writeAttribute("align", align)
		xml.writeAttribute("rotation", str(rotation))
		xml.writeEndElement() #fecha font
		
	def getFont(node: QDomNode):
		if node.nodeName() != "font":
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("family") and attr.contains("size")):
			return None
		ans = PFSAux()
		ans.font = QFont(attr.namedItem("family").nodeValue(), int(attr.namedItem("size").nodeValue()))
		if attr.contains("style"):
			if attr.namedItem("style").nodeValue() == "italic":
				ans.font.setStyle(QFont.StyleItalic)
			elif attr.namedItem("style").nodeValue() == "oblique":
				ans.font.setStyle(QFont.StyleOblique)
		if attr.contains("weight"):
			v = ["bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900", "900"]
			if attr.namedItem("weight").nodeValue() in v:
				ans.font.setWeight(v.index(attr.namedItem("weight").nodeValue())*4+50)
		if attr.contains("decoration"):
			decor = attr.namedItem("decoration").nodeValue()
			if decor.find("underline") > 0:
				ans.font.setUnderline(True)
			if decor.find("overline") > 0:
				ans.font.setOverline(True)
			if decor.find("line-through") > 0:
				ans.font.setStrikeOut(True)
		if attr.contains("align"):
			ans.align = attr.namedItem("align").nodeValue()
		else:
			ans.align = None
		if attr.contains("rotation"):
			ans.rotation = int(attr.namedItem("rotation").nodeValue())
		else:
			ans.rotation = None
		return ans
	
	def line(xml: QXmlStreamWriter, pen: QPen, tag: str="line"):
		xml.writeStartElement(tag)
		xml.writeAttribute("color", pen.color().name())
		xml.writeAttribute("width", str(pen.width()))
		if pen.style() == Qt.DashLine:
			xml.writeAttribute("style", "dash")
		elif pen.style() == Qt.DotLine:
			xml.writeAttribute("style", "dot")
		else:
			xml.writeAttribute("style", "solid")
		xml.writeEndElement() #fecha line
		
	def getLine(node: QDomNode):
		if node.nodeName() not in ["line"]:
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("color")):
			return None
		pen = QPen(QColor(attr.namedItem("color").nodeValue()))
		if attr.contains("width"):
			pen.setWidth(int(attr.namedItem("width").nodeValue()))
		if attr.contains("style"):
			if attr.namedItem("style").nodeValue() == "dash":
				pen.setStyle(Qt.DashLine)
			if attr.namedItem("style").nodeValue() == "dot":
				pen.setStyle(Qt.DotLine)
		return pen
		
	def fill(xml: QXmlStreamWriter, brush: QBrush, tag: str="fill"):
		xml.writeStartElement(tag)
		if brush.gradient() is not None and brush.gradient().type() != QGradient.NoGradient:
			grad = brush.gradient()
			if grad.type() != QGradient.LinearGradient:
				xml.writeAttribute("gradient-rotation", "diagonal")
			else:
				if grad.start().x() == grad.finalStop().x():
					xml.writeAttribute("gradient-rotation", "vertical")
				elif grad.start().y() == grad.finalStop().y():
					xml.writeAttribute("gradient-rotation", "horizontal")
				else:
					xml.writeAttribute("gradient-rotation", "diagonal")
			xml.writeAttribute("color", grad.stops()[0][1].name())
			xml.writeAttribute("gradient-color", grad.stops()[1][1].name())
		else:
			xml.writeAttribute("color", brush.color().name())
		xml.writeEndElement() #fecha fill
		
	def getFill(node: QDomNode):
		if node.nodeName() != "fill":
			return None
		attr = node.attributes()
		if not (node.hasAttributes() and attr.contains("color")):
			return None
		brush = QBrush(Qt.black, Qt.SolidPattern)
		brush.setColor(QColor(attr.namedItem("color").nodeValue()))
		return brush
	
	def graphicsNode(xml: QXmlStreamWriter, rect: QRect, pen: QPen, brush: QBrush):
		xml.writeStartElement("graphics")
		PFSXmlBase.position(xml, rect.x(), rect.y())
		PFSXmlBase.position(xml, rect.width(), rect.height(), "dimension")
		if brush is not None:
			PFSXmlBase.fill(xml, brush)
		if pen is not None:
			PFSXmlBase.line(xml, pen)
		xml.writeEndElement() #fecha graphics
	
	def getNode(node: QDomNode):
		if node.nodeName() != "graphics":
			return None
		x = None
		y = None
		w = None
		h = None
		brush = None
		line = None
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "position":
				pos = PFSXmlBase.getPosition(child)
				if pos is not None:
					x = pos.x
					y = pos.y
			if child.nodeName() == "dimension":
				pos = PFSXmlBase.getPosition(child)
				if pos is not None:
					w = pos.x
					h = pos.y
			if child.nodeName() == "fill":
				brush = PFSXmlBase.getFill(child)
			if child.nodeName() == "line":
				line = PFSXmlBase.getLine(child)
		if x is None or y is None or w is None or h is None:
			return None
		ans = PFSAux()
		ans.rect = QRect(x, y, w, h)
		ans.line = line
		ans.brush = brush
		return ans
	
	def graphicsArc(xml: QXmlStreamWriter, points: [QPoint], pen: QPen):
		xml.writeStartElement("graphics")
		for p in points:
			PFSXmlBase.position(xml, p.x(), p.y())
		if pen is not None:
			PFSXmlBase.line(xml, pen)
		xml.writeEndElement() #fecha graphics
	
	def getArc(node: QDomNode):
		if node.nodeName() != "graphics":
			return None
		p = []
		line = None
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "position":
				pos = PFSXmlBase.getPosition(child)
				if pos is not None:
					p.append(pos)
			if child.nodeName() == "line":
				line = PFSXmlBase.getLine(child)
		ans = PFSAux()
		ans.pos = p
		ans.line = line
		return ans
		
	def graphicsText(xml: QXmlStreamWriter, x: int, y: int, font: QFont, pen: QPen, brush: QBrush, align: str, rotation: int):
		xml.writeStartElement("graphics")
		PFSXmlBase.position(xml, x, y, "offset")
		if font is None:
			font = PFSXmlBase.STANDARDTEXTFONT
		PFSXmlBase.font(xml, font, align)
		if brush is not None:
			PFSXmlBase.fill(xml, brush)
		if pen is not None:
			PFSXmlBase.line(xml, pen)
		xml.writeEndElement() #fecha graphics
	
	def getGraphicsText(node: QDomNode):
		x = None
		y = None
		font = None
		brush = None
		line = None
		align = None
		rotation = None
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "offset":
				pos = PFSXmlBase.getPosition(child)
				if pos is not None:
					x = pos.x
					y = pos.y
			if child.nodeName() == "font":
				f = PFSXmlBase.getFont(child)					
				if f is not None:
					font = f.font
					align = f.align
					rotation = f.rotation
			if child.nodeName() == "fill":
				brush = PFSXmlBase.getFill(child)
			if child.nodeName() == "line":
				line = PFSXmlBase.getLine(child)
		if x is None or y is None:
			return None
		ans = PFSAux()
		ans.x = x
		ans.y = y
		ans.font = font
		ans.align = align
		ans.rotation = rotation
		ans.line = line
		ans.brush = brush
		return ans		
		
	def text(xml: QXmlStreamWriter, text: str, x: int, y: int, font: QFont= None, rotation: int=0, pen: QPen=None, brush: QBrush=None, tag: str="name", align: str="left"):
		xml.writeStartElement(tag)
		xml.writeStartElement("annotation")
		xml.writeCharacters(text)
		xml.writeEndElement() #fecha annotation
		PFSXmlBase.graphicsText(xml, x, y, font, pen, brush, align, rotation)
		xml.writeEndElement() #fecha text	
		
	def getText(node: QDomNode):
		graphics = None
		text = None
		childs = node.childNodes()
		for i in range(childs.count()):
			child = childs.at(i)
			if child.nodeName() == "annotation":
				text = child.toElement().text()
			if child.nodeName() == "graphics":
				graphics = PFSXmlBase.getGraphicsText(child)
		if text is None or graphics is None:
			return None
		ans = PFSAux()
		ans.annotation = text
		ans.x = graphics.x
		ans.y = graphics.y
		ans.font = graphics.font
		ans.align = graphics.align
		ans.rotation = graphics.rotation
		ans.line = graphics.line
		ans.brush = graphics.brush
		return ans