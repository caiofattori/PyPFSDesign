
class PFSXmlBase:
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
			family = "Helvetica"
			size = "12"
		else:
			family = font.family()
			size = str(font.pointSize())
		xml.writeAttribute("family", family)
		xml.writeAttribute("size", size)
		xml.writeEndElement() #fecha font
		if pen is not None:
			xml.writeStartElement("line")
			xml.writeAttribute("color", pen.color().toString())
			xml writeEndElement()
		xml.writeStartElement(tagPos)
		xml.writeAttribute("x", str(x))
		xml.writeAttribute("y", str(y))
		xml.writeEndElement()
			
		xml.writeEndElement() #fecha graphics
		xml.writeEndElement() #fecha text
		