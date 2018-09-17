
class PFSActivityContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._text = None
		self._width = None
		self._height = None
		self._textFont = None
		self._fontMetrics = None
		self._pen = None
		self._brush = None
		self._tags = None
		self._outputNum = None
		self._inputNum = None

class PFSOpenActivityContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._h = None
		self._tags = None

class PFSCloseActivityContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._h = None
		self._tags = None

class PFSDistributorContent(object):
	def __init__(self):
		self._id = None
		self._x = None
		self._y = None
		self._width = None
		self._height = None
		self._pen = None
		self._brush = None
		self._tags = None

class PFSPageContent(object):
	def __init__(self):
		self._id = None
		self._mainpage = None
		self._ref = None
		self._width = None
		self._height = None
		self._tags = None
		self._activities = None
		self._openActivities = None
		self._closeActivities = None
		self._distributors = None
		self._relations = None

class PFSRelationContent(object):
	def __init__(self):
		self._id = None
		self._source = None
		self._target = None
		self._midPoints = None
		self._pen = None
		self._tags = None
		