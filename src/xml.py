from PyQt5.QtGui import QFont, QGradient
from PyQt5.QtCore import Qt

class PFSXmlBase:
	STANDARDTEXTFONT = QFont("Helvetica", 12)
	def open(xml):
		xml.writeStartElement("toolspecific")
		xml.writeAttribute("tool", "PFS")
		xml.writeAttribute("version", "1.0.0")
		
	def close(xml):
		xml.writeEndElement()
		
	def text(xml, text, x, y, font= None, pen=None, tag="name", tagPos="offset"):
		xml.writeStartElement(tag)
		xml.writeStartElement("annotation")
		xml.writeCharacters(text)
		xml.writeEndElement() #fecha annotation
		xml.writeStartElement("graphics")
		xml.writeStartElement("font")
		if font is None:
			font = PFSXmlBase.STANDARDTEXTFONT
		xml.writeAttribute("family", font.family())
		xml.writeAttribute("size", str(font.pointSize()))
		xml.writeEndElement() #fecha font
		if pen is not None:
			xml.writeStartElement("line")
			xml.writeAttribute("color", pen.color().toString())
			xml.writeEndElement()
		xml.writeStartElement(tagPos)
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement()
		xml.writeEndElement() #fecha graphics
		xml.writeEndElement() #fecha text
	
	def graphicsText(xml, x, y, font, pen, brush):
		xml.writeStartElement("graphics")
		xml.writeStartElement("offset")
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement() #fecha pos
		if font is None:
			font = PFSXmlBase.STANDARDTEXTFONT
		xml.writeStartElement("font")
		xml.writeAttribute("family", font.family())
		if font.style() == QFont.StyleItalic:
			xml.writeAttribute("style", "italic")
		elif font.style() == QFont.StyleOblique:
			xml.writeAttribute("style", "oblique")
		else:
			xml.writeAttribute("style", "normal")
		xml.writeAttribute("size", str(font.pointSize()))
		xml.writeEndElement() #fecha font
			
		if brush is not None:
			xml.writeStartElement("fill")
			if brush.gradient().type() != QGradient.NoGradient:
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
				xml.writeAttribute("color", grad.stops()[0][1].rgb())
				xml.writeAttribute("gradient-color", grad.stops()[1][1].rgb())
			elif brush.textureImage() is not None:
				xml.writeAttribute("image", brush.textureImage().uri())
			else:
				xml.writeAttribute("color", brush.color().rgb())
			xml.writeEndElement() #fecha fill
		if pen is not None:
			xml.writeStartElement("line")
			xml.writeAttribute("color", pen.color().rgb())
			xml.writeAttribute("width", str(pen.width()))
			if pen.style() == Qt.DashLine:
				xml.writeAttribute("style", "dash")
			elif pen.style() == Qt.DotLine:
				xml.writeAttribute("style", "dot")
			else:
				xml.writeAttribute("style", "solid")
			xml.writeEndElement() #fecha line
		xml.writeEndElement() #fecha graphics	
	
	def graphicsNode(xml, rect, pen, brush):
		xml.writeStartElement("graphics")
		xml.writeStartElement("position")
		xml.writeAttribute("x", str(rect.x()))
		xml.writeAttribute("y", str(rect.y()))
		xml.writeEndElement() #fecha pos
		xml.writeStartElement("dimension")
		xml.writeAttribute("x", str(rect.width()))
		xml.writeAttribute("y", str(rect.height()))
		xml.writeEndElement() #fecha dimension
		if brush is not None:
			xml.writeStartElement("fill")
			if brush.gradient().type() != QGradient.NoGradient:
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
				xml.writeAttribute("color", grad.stops()[0][1].rgb())
				xml.writeAttribute("gradient-color", grad.stops()[1][1].rgb())
			elif brush.textureImage() is not None:
				xml.writeAttribute("image", brush.textureImage().uri())
			else:
				xml.writeAttribute("color", brush.color().rgb())
			xml.writeEndElement() #fecha fill
		if pen is not None:
			xml.writeStartElement("line")
			xml.writeAttribute("color", pen.color().rgb())
			xml.writeAttribute("width", str(pen.width()))
			if pen.style() == Qt.DashLine:
				xml.writeAttribute("style", "dash")
			elif pen.style() == Qt.DotLine:
				xml.writeAttribute("style", "dot")
			else:
				xml.writeAttribute("style", "solid")
			xml.writeEndElement() #fecha line
		xml.writeEndElement() #fecha graphics