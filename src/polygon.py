import math
from PyQt5.QtCore import QPointF

class PFSPolygon(object):
	def __init__(self):
		self._angle = 0
		self._x = 0
		self._y = 0
		
	def setPoint(self, x, y):
		self._x = x
		self._y = y
		
	def setAngle(self, a):
		self._angle = a*math.pi/180
	
	def translate(self, a):
		self._angle = self._angle + a*math.pi/180
	
	def move(self, d):
		self._x = self._x + d*math.cos(self._angle)
		self._y = self._y + d*math.sin(self._angle)
		return QPointF(self._x, self._y)