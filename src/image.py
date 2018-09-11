from PyQt5.QtGui import QImage, QPainter, QIconEngine
from PyQt5.QtCore import QSize, QRect, Qt
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
		
class PFSDistributorIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):
		p.drawEllipse(r)
		
class PFSActivityIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):
		p.drawText(r, Qt.AlignCenter, "[Ac]")
		
class PFSRelationIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):		
		p.drawLine(r.left(), r.bottom(), r.right(), r.top())
		p.drawLine(r.right() - 7, r.top() + 4, r.right(), r.top())
		p.drawLine(r.right() - 4, r.top() + 7, r.right(), r.top())
		
class PFSPageIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):
		p.drawRect(r)
		y = r.height()/4
		p.drawLine(r.left()+2, r.top()+y, r.right()-2, r.top()+y)
		p.drawLine(r.left()+2, r.top()+2*y, r.right()-2, r.top()+2*y)
		p.drawLine(r.left()+2, r.top()+3*y, r.right()-2, r.top()+3*y)
		
class PFSOpenActivityIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):
		p.drawLine(r.left()+1, r.top()+1, r.left()+5, r.top()+1)
		p.drawLine(r.left()+1, r.top()+1, r.left()+1, r.bottom()-1)
		p.drawLine(r.left()+1, r.bottom()-1, r.left()+5, r.bottom()-1)
		
class PFSCloseActivityIcon(QIconEngine):
	def __init__(self):
		QIconEngine.__init__(self)
		
	def paint(self, p, r, m, s):
		p.drawLine(r.right()-1, r.top()+1, r.right()-5, r.top()+1)
		p.drawLine(r.right()-1, r.top()+1, r.right()-1, r.bottom()-1)
		p.drawLine(r.right()-1, r.bottom()-1, r.right()-5, r.bottom()-1)