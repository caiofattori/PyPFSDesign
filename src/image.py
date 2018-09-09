from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QSize, QRect
try:
	from PyQt5.QtSvg import QSvgGenerator
	hasSvg = True
except:
	hasSvg = False
	
class PFSImage(object):
	
	def __init__(self):
		pass
		
	def gravaSvg(scene, filename):
		if not hasSvg:
			return False
		aux = scene._paintGrid
		scene._paintGrid = False
		scene.clearSelection()
		svg = QSvgGenerator()
		svg.setFileName(filename)
		svg.setSize(QSize(scene.width(), scene.height()))
		svg.setViewBox(QRect(0, 0, scene.width(), scene.height()))
		painter = QPainter()
		painter.begin(svg)
		scene.render(painter)
		painter.end()
		scene._paintGrid = aux
		return True
		
	def gravaPng(scene, filename):
		aux = scene._paintGrid
		scene._paintGrid = False
		scene.clearSelection()
		img = QImage(scene.width(), scene.height(), QImage.Format_ARGB32_Premultiplied)
		painter = QPainter()
		painter.begin(img)
		scene.render(painter)
		painter.end()
		img.save(filename)
		scene._paintGrid = aux
		return True