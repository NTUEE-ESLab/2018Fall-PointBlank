#!/usr/bin/python3
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import json

class Window(QtWidgets.QWidget):
	def __init__(self, app):
		super().__init__()
		self.app = app
		self.fd = os.open("settings.dat", os.O_RDWR|os.O_CREAT)
		self.readSettings()

		self.screenshot = app.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
		if 740.0/self.screenshot.width() > 500.0/self.screenshot.height():
			self.factor = 500.0/self.screenshot.height()
		else:
			self.factor = 740.0/self.screenshot.width()
		
		self.setWindowTitle("PointBlank settings")
		self.resize(800, 800)
		self.setup()
		self.show()

	def setup(self):
		self.canvas = Canvas(self.r, self.width, self.color, self.multiplier, self.screenshot, self.factor, self)
		self.canvas.setGeometry(QtCore.QRect(30, 0, 740, 500))

		self.centralWidget = QtWidgets.QWidget(self)
		self.verticalWidget = QtWidgets.QWidget(self.centralWidget)
		self.verticalWidget.setGeometry(QtCore.QRect(30, 500, 740, 300))
		self.vertical = QtWidgets.QVBoxLayout(self.verticalWidget)
		self.vertical.setSpacing(5)

		self.horizon1 = QtWidgets.QHBoxLayout()
		self.horizon1.setContentsMargins(200, 0, 200, 0)
		self.button1 = QtWidgets.QPushButton("Change Color", self.verticalWidget)
		self.button2 = QtWidgets.QPushButton("Change Mode", self.verticalWidget)
		self.horizon1.addWidget(self.button1)
		self.horizon1.addWidget(self.button2)
		
		self.label1 = QtWidgets.QLabel("Circle Size", self.verticalWidget)
		self.label1.setIndent(3)

		self.slider1 = QtWidgets.QSlider(self.verticalWidget)
		self.slider1.setTracking(True)
		self.slider1.setMinimum(5)
		self.slider1.setMaximum(300)
		self.slider1.setSingleStep(10)
		self.slider1.setPageStep(50)
		self.slider1.setProperty("value", self.r)
		self.slider1.setOrientation(QtCore.Qt.Horizontal)
		self.slider1.setTickPosition(QtWidgets.QSlider.TicksBothSides)
		self.slider1.setTickInterval(50)

		self.label2 = QtWidgets.QLabel("Ring Width", self.verticalWidget)
		self.label2.setIndent(3)

		self.slider2 = QtWidgets.QSlider(self.verticalWidget)
		self.slider2.setTracking(True)
		self.slider2.setMinimum(1)
		self.slider2.setMaximum(30)
		self.slider2.setSingleStep(1)
		self.slider2.setPageStep(5)
		self.slider2.setProperty("value", self.width)
		self.slider2.setOrientation(QtCore.Qt.Horizontal)
		self.slider2.setTickPosition(QtWidgets.QSlider.TicksBothSides)
		self.slider2.setTickInterval(5)

		self.label3 = QtWidgets.QLabel("Magnification Multiplier", self.verticalWidget)
		self.label3.setIndent(3)

		self.slider3 = QtWidgets.QSlider(self.verticalWidget)
		self.slider3.setTracking(True)
		self.slider3.setMinimum(10)
		self.slider3.setMaximum(100)
		self.slider3.setSingleStep(1)
		self.slider3.setPageStep(10)
		self.slider3.setProperty("value", self.multiplier*10)
		self.slider3.setOrientation(QtCore.Qt.Horizontal)
		self.slider3.setTickPosition(QtWidgets.QSlider.TicksBothSides)
		self.slider3.setTickInterval(10)

		self.horizon2 = QtWidgets.QHBoxLayout()
		self.button3 = QtWidgets.QPushButton("Save", self.verticalWidget)
		self.button4 = QtWidgets.QPushButton("Reset", self.verticalWidget)
		self.button5 = QtWidgets.QPushButton("Close", self.verticalWidget)
		self.horizon2.addWidget(self.button3)
		self.horizon2.addWidget(self.button4)
		self.horizon2.addWidget(self.button5)

		self.vertical.addLayout(self.horizon1)
		self.vertical.addWidget(self.label1)
		self.vertical.addWidget(self.slider1)
		self.vertical.addWidget(self.label2)
		self.vertical.addWidget(self.slider2)
		self.vertical.addWidget(self.label3)
		self.vertical.addWidget(self.slider3)
		self.vertical.addLayout(self.horizon2)

		self.slider1.valueChanged.connect(self.canvas.changeR)
		self.slider2.valueChanged.connect(self.canvas.changeWidth)
		self.slider3.valueChanged.connect(self.canvas.changeMultiplier)
		self.button1.clicked.connect(self.askColor)
		self.button2.clicked.connect(self.canvas.changeMode)
		self.button3.clicked.connect(self.writeSettings)
		self.button4.clicked.connect(self.reset)
		self.button5.clicked.connect(self.quit)

	def quit(self):
		os.close(self.fd)
		self.app.quit()

	def askColor(self):
		color = QtWidgets.QColorDialog.getColor(self.canvas.color, self, "Choose a Color", QtWidgets.QColorDialog.ShowAlphaChannel | QtWidgets.QColorDialog.DontUseNativeDialog)
		if color.isValid():
			self.canvas.changeColor(color)

	def reset(self):
		self.readSettings()
		self.slider1.setValue(self.r)
		self.slider2.setValue(self.width)
		self.slider3.setValue(self.multiplier*10)
		self.canvas.changeR(self.r)
		self.canvas.changeWidth(self.width)
		self.canvas.changeColor(self.color)

	def readSettings(self):
		os.lseek(self.fd, 0, os.SEEK_SET)
		buf = os.read(self.fd, 256)
		if buf:
			args = json.loads(buf.decode())
			self.r = args[0]
			self.width = args[1]
			self.color = QtGui.QColor(args[2][0],args[2][1],args[2][2],args[2][3])
			self.multiplier = args[3]
		else:
			self.r = 100
			self.width = 5
			self.color = QtGui.QColor(100,100,100,200)
			self.multiplier = 2

	def writeSettings(self):
		buf = [self.canvas.r, self.canvas.width, self.canvas.color.getRgb(), self.canvas.multiplier]
		args = json.dumps(buf)
		os.lseek(self.fd, 0, os.SEEK_SET)
		os.write(self.fd, args.encode())
		os.ftruncate(self.fd, len(args.encode()))

class Canvas(QtWidgets.QWidget):
	def __init__(self, r, width, color, multiplier, screenshot, scale, parent):
		super().__init__(parent)
		self.r = r
		self.width = width
		self.mode = "laser"
		self.point = QtCore.QPoint(370, 250)
		self.color = color
		self.multiplier = multiplier
		self.screenshot = screenshot
		self.factor = scale
		self.smallScreenshot = screenshot.scaled(screenshot.size()*scale)
		self.align = [int((740-self.smallScreenshot.width())/2), int((500-self.smallScreenshot.height())/2)]
		self.update()

	def paintEvent(self, event):

		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.drawPixmap(self.align[0], self.align[1], self.smallScreenshot)
		r = int(self.r*self.factor)
		width = int(self.width*self.factor)

		if self.mode == "laser":
			pen = QtGui.QPen(self.color)
			pen.setWidth(width)
			painter.setPen(pen)
			painter.drawArc(370-r,250-r,2*r,2*r, 0, 5760);

		elif self.mode == "highlight":
			path = QtGui.QPainterPath()
			path.addRect(QtCore.QRectF(self.align[0],self.align[1],self.smallScreenshot.width(),self.smallScreenshot.height()))
			path.addEllipse(self.point, r, r)
			painter.fillPath(path, self.color)

		elif self.mode == "magnify":
			bigScreenshot = self.screenshot.scaled(self.multiplier*self.factor*self.screenshot.size())
			painter.setClipRegion(QtGui.QRegion((self.point.x() - r), (self.point.y() - r), 2*r, 2*r, QtGui.QRegion.Ellipse))
			painter.setClipping(True)
			painter.translate(-(self.multiplier - 1)*self.point)
			painter.drawPixmap(self.multiplier*self.align[0],self.multiplier*self.align[1], bigScreenshot)
			painter.setClipping(False)
			pen = QtGui.QPen(self.color)
			pen.setWidth(width)
			painter.setPen(pen)
			painter.translate((self.multiplier - 1)*self.point)
			painter.drawEllipse(self.point, r, r)

	def changeMode(self):
		if self.mode == "laser":
			self.mode = "highlight"

		elif self.mode == "highlight":
			self.mode = "magnify"

		elif self.mode == "magnify":
			self.mode = "laser"

		self.update()

	def changeR(self, r):
		self.r = r
		self.update()

	def changeWidth(self, width):
		self.width = width
		self.update()

	def changeColor(self, color):
		self.color = color
		self.update()

	def changeMultiplier(self, multiplier):
		self.multiplier = multiplier/10
		self.update()



if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	window = Window(app)

	sys.exit(app.exec())