from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QDialogButtonBox

class PFSDialogTag(QDialog):
	def __init__(self, name="", use=""):
		QDialog.__init__(self)
		layout = QVBoxLayout()
		self.setLayout(layout)		
		self.nameLine = QLineEdit(name)
		self.useLine = QLineEdit(use)
		hl = QHBoxLayout()
		hl.addWidget(QLabel("Uso"))
		hl.addWidget(self.useLine)
		layout.addLayout(hl)
		hl = QHBoxLayout()
		hl.addWidget(QLabel("Conteúdo"))		
		hl.addWidget(self.nameLine)
		layout.addLayout(hl)
		button = QDialogButtonBox()
		button.addButton(QDialogButtonBox.Cancel)
		button.addButton(QDialogButtonBox.Ok)
		button.accepted.connect(self.accept)
		button.rejected.connect(self.reject)
		layout.addWidget(button)
		
	def getTag(name="", use=""):
		dial = PFSDialogTag(name, use)
		ans = dial.exec_()
		if ans:
			return dial.nameLine.text(), dial.useLine.text(), ans
		return "", "", ans