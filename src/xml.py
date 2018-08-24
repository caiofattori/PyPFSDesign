from PyQt5.QtGui import QFont, QGradient, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QRect, QXmlStreamReader, QXmlStreamWriter

class PFSAux:
	def __init__(self):
		pass

class PFSXmlBase:
	STANDARDTEXTFONT = QFont("Helvetica", 12)
	def open(xml: QXmlStreamWriter):
		xml.writeStartElement("toolspecific")
		xml.writeAttribute("tool", "PFS")
		xml.writeAttribute("version", "1.0.0")
	
	def nextTool(xml: QXmlStreamReader):
		if xml.name() == "toolspecific":
			if xml.attributes().value("tool") == "PFS" and xml.attributes().value("version") == "1.0.0":
				xml.readNextStartElement()
				return True
		xml.readNextStartElement()
		if xml.name() == "toolspecific":
			if xml.attributes().value("tool") == "PFS" and xml.attributes().value("version") == "1.0.0":
				xml.readNextStartElement()
				return True
		return False
				
	def close(xml: QXmlStreamWriter):
		xml.writeEndElement()
		
	def position(xml: QXmlStreamWriter, x: int, y: int, tag: str="position"):
		xml.writeStartElement(tag)
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement() #fecha pos
		
	def getPosition(xml: QXmlStreamReader):
		xml.readNextStartElement()
		attr = xml.attributes()
		if not (attr.hasAttribute("x") and attr.hasAttribute("y")):
			return None
		ans = PFSAux()
		ans.x = int(attr.value("x"))
		ans.y = int(attr.value("y"))
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
		
	def getFont(xml: QXmlStreamReader):
		xml.readNextStartElement()
		attr = xml.attributes()
		if not (attr.hasAttribute("family") and attr.hasAttribute("size")):
			return None
		font = QFont(attr.value("family"), int(attr.value("size")))
		align = None
		rotation = None
		if attr.hasAttribute("style"):
			if attr.value("style") == "italic":
				font.setStyle(QFont.StyleItalic)
			elif attr.value("style") == "oblique":
				font.setStyle(QFont.StyleOblique)
		if attr.hasAttribute("weight"):
			v = ["bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900", "900"]
			if attr.value("weight") in v:
				font.setWeight(v.index(attr.value("weight"))*4+50)
		if attr.hasAttribute("decoration"):
			if attr.value("decoration").find("underline") > 0:
				font.setUnderline(True)
			if attr.value("decoration").find("overline") > 0:
				font.setOverline(True)
			if attr.value("decoration").find("line-through") > 0:
				font.setStrikeOut(True)
		if attr.hasAttribute("align"):
			align = attr.value("align")
		if attr.hasAttribute("rotation"):
			rotation = attr.value("rotation")		
		ans = PFSAux()
		ans.font = font
		ans.align = align
		ans.rotation = rotation
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
		
	def getLine(xml: QXmlStreamReader):
		xml.readNextStartElement()
		attr = xml.attributes()
		if not attr.hasAttribute("color"):
			return None
		pen = QPen(QColor(attr.value("color")))
		if attr.hasAttribute("width"):
			pen.setWidth(int(attr.value("width")))
		if attr.hasAttribute("style"):
			if attr.value("style") == "dash":
				pen.setStyle(Qt.DashLine)
			if attr.value("style") == "dot":
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
		#elif brush.textureImage() is not None:
		#	xml.writeAttribute("image", brush.textureImage().uri())
		else:
			xml.writeAttribute("color", brush.color().name())
		xml.writeEndElement() #fecha fill
		
	def getFill(xml: QXmlStreamReader):
		xml.readNextStartElement()
		attr = xml.attributes()
		if not attr.hasAttribute("color"):
			return None
		brush = QBrush()
		brush.setColor(QColor(attr.value("color")))
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
	
	def getNode(xml: QXmlStreamReader):
		xml.readNextStartElement()
		x = None
		y = None
		w = None
		h = None
		brush = None
		line = None
		while xml.name() in ["position", "dimension", "fill", "line"]:
			if xml.name() == "position":
				pos = PFSXmlBase.getPosition(xml)
				if pos is not None:
					x = pos.x
					y = pos.y
			if xml.name() == "dimension":
				pos = PFSXmlBase.getPosition(xml)
				if pos is not None:
					w = pos.x
					h = pos.y
			if xml.name() == "fill":
				brush = PFSXmlBase.getFill(xml)
			if xml.name() == "line":
				line = PFSXmlBase.getLine(xml)
			xml.readNextStartElement()
		if x is None or y is None or w is None or h is None:
			return None
		ans = PFSAux()
		ans.rect = QRect(x, y, w, h)
		ans.line = line
		ans.brush = brush
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
	
	def getGraphicsText(xml: QXmlStreamReader):
		xml.readNextStartElement()
		x = None
		y = None
		font = None
		brush = None
		line = None
		align = None
		rotation = None
		while xml.name() in ["offset", "font", "fill", "line"]:
			if xml.name() == "offset":
				pos = PFSXmlBase.getPosition(xml)
				if pos is not None:
					x = pos.x
					y = pos.y
			if xml.name() == "font":
				f = PFSXmlBase.getFont(xml)					
				if f is not None:
					font = f.font
					align = f.align
					rotation = f.rotation
			if xml.name() == "fill":
				brush = PFSXmlBase.getFill(xml)
			if xml.name() == "line":
				line = PFSXmlBase.getLine(xml)
			xml.readNextStartElement()
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
		
	def getText(xml: QXmlStreamReader):
		xml.readNextStartElement()
		graphics = None
		text = None
		while xml.name() in ["graphics", "annotation"]:
			if xml.name() == "annotation":
				text = xml.text()
			else:
				graphics = PFSXmlBase.getGraphicsText(xml)
			xml.readNextStartElement()
		if text is None or graphics is None:
			return None
		ans = PFSAux()
		ans.text = text
		ans.x = graphics.x
		ans.y = graphics.y
		ans.font = graphics.font
		ans.align = graphics.align
		ans.rotation = graphics.rotation
		ans.line = graphics.line
		ans.brush = graphics.brush		
		return ans