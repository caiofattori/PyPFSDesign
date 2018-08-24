from PyQt5.QtGui import QFont, QGradient
from PyQt5.QtCore import Qt

class PFSXmlBase:
	STANDARDTEXTFONT = QFont("Helvetica", 12)
	def open(xml):
		xml.writeStartElement("toolspecific")
		xml.writeAttribute("tool", "PFS")
		xml.writeAttribute("version", "1.0.0")
	
	def nextTool(xml):
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
				
	def close(xml):
		xml.writeEndElement()
		
	def position(xml, x, y, tag="position"):
		xml.writeStartElement(tag)
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement() #fecha pos
		
	def font(xml, font, align="left", rotation=0, tag="font"):
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
	
	def line(xml, pen, tag="line"):
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
		
	def fill(xml, brush, tag="fill"):
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
	
	def graphicsNode(xml, rect, pen, brush):
		xml.writeStartElement("graphics")
		PFSXmlBase.position(xml, rect.x(), rect.y())
		PFSXmlBase.position(xml, rect.width(), rect.height(), "dimension")
		if brush is not None:
			PFSXmlBase.fill(xml, brush)
		if pen is not None:
			PFSXmlBase.line(xml, pen)
		xml.writeEndElement() #fecha graphics
		
	def graphicsText(xml, x, y, font, pen, brush, align, rotation):
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
		
	def text(xml, text, x, y, font= None, rotation=0, pen=None, brush=None, tag="name", align="left"):
		xml.writeStartElement(tag)
		xml.writeStartElement("annotation")
		xml.writeCharacters(text)
		xml.writeEndElement() #fecha annotation
		PFSXmlBase.graphicsText(xml, x, y, font, pen, brush, align, rotation)
		xml.writeEndElement() #fecha text
		