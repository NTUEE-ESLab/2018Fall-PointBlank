import sys
import random
from PyQt5 import QtWidgets, QtCore, QtGui

class Canvas(QtWidgets.QWidget):
	def __init__(self, app, r, mode):
		super().__init__()

		self.setGeometry(app.primaryScreen().geometry())
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)		
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)

		self.app = app
		self.point = app.primaryScreen().geometry().center()
		self.r = r
		self.mode = mode
		self.primaryColor = QtGui.QColor(100,100,100,200)

		self.moveTimer = self.startTimer(16)
		self.modeTimer = self.startTimer(1000)
		self.quitTimer = self.startTimer(5000)

		#self.showFullScreen()
		self.show()

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		if self.mode == "laser":
			painter.setBrush(self.primaryColor)
		elif self.mode == "highlight":
			painter.setBrush(QtCore.Qt.transparent)
			painter.fillRect(self.app.primaryScreen().geometry(),self.primaryColor)

		painter.drawEllipse(self.point, self.r, self.r)
	
	def timerEvent(self, event):
		if event.timerId() == self.moveTimer:
			self.point = self.mapFromGlobal(QtGui.QCursor.pos())
			self.update()
		elif event.timerId() == self.modeTimer:
			self.changeMode()
			self.update()

		elif event.timerId() == self.quitTimer:
			self.app.quit()

	def changeMode(self):
		if self.mode == "laser":
			self.mode = "highlight"

		elif self.mode == "highlight":
			self.mode = "laser"


if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	r = 100
	mode = "laser"
	canvas = Canvas(app, r, mode)

	app.exec()
	#sys.exit(app.exec_())