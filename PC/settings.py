from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import sys
import os
import json

class Window(QtWidgets.QWidget):
	def __init__(self, app):
		super().__init__()
		self.app = app
		self.fd = os.open("settings.dat", os.O_RDWR|os.O_CREAT)
		self.readSettings()

		sc = app.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
		if 740.0/sc.width() > 600.0/sc.height():
			self.factor = 600.0/sc.height()
		else:
			self.factor = 740.0/sc.width()
		self.screenshot = sc.scaled(int(sc.width()*self.factor), int(sc.height()*self.factor))
		
		self.setWindowTitle("PointBlank settings")
		self.resize(800, 800)
		self.setup()
		self.show()

	def setup(self):
		self.canvas = Canvas(self.r, self.width, self.color, self.screenshot, self.factor, self)
		self.canvas.setGeometry(QtCore.QRect(30, 0, 740, 600))

		self.centralWidget = QtWidgets.QWidget(self)
		self.verticalWidget = QtWidgets.QWidget(self.centralWidget)
		self.verticalWidget.setGeometry(QtCore.QRect(30, 600, 740, 180))
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
		self.vertical.addLayout(self.horizon2)

		self.slider1.valueChanged.connect(self.canvas.changeR)
		self.slider2.valueChanged.connect(self.canvas.changeWidth)
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
		else:
			self.r = 100
			self.width = 5
			self.color = QtGui.QColor(100,100,100,200)

	def writeSettings(self):
		buf = [self.canvas.r, self.canvas.width, self.canvas.color.getRgb()]
		args = json.dumps(buf)
		os.lseek(self.fd, 0, os.SEEK_SET)
		os.write(self.fd, args.encode())
		os.ftruncate(self.fd, len(args.encode()))

class Canvas(QtWidgets.QWidget):
	def __init__(self, r, width, color, screenshot, scale, parent):
		super().__init__(parent)
		self.r = r
		self.width = width
		self.mode = "laser"
		self.point = QtCore.QPoint(370, 300)
		self.color = color
		self.screenshot = screenshot
		self.factor = scale
		self.align = [int((740-screenshot.width())/2), int((600-screenshot.height())/2)]
		self.update()

	def paintEvent(self, event):

		painter = QtGui.QPainter(self)
		painter.drawPixmap(self.align[0], self.align[1], self.screenshot)
		r = int(self.r*self.factor)
		width = int(self.width*self.factor)

		if self.mode == "laser":
			pen = QtGui.QPen(self.color)
			pen.setWidth(width)
			painter.setPen(pen)
			painter.drawArc(370-r,300-r,2*r,2*r, 0, 5760);

		elif self.mode == "highlight":
			path = QtGui.QPainterPath()
			path.addRect(QtCore.QRectF(self.align[0],self.align[1],self.screenshot.width(),self.screenshot.height()))
			path.addEllipse(self.point, r, r)
			painter.fillPath(path, self.color)

	def changeMode(self):
		if self.mode == "laser":
			self.mode = "highlight"

		elif self.mode == "highlight":
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



if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	window = Window(app)

	sys.exit(app.exec())