from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import pyautogui
import random
import sys

import ble_client

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
		self.visible = False

		self.ble = ble_client.PointBlankBleClient(self)

	def start(self):
		print("ble setup finished")
		self.moveTimer = self.startTimer(20)
		# self.quitTimer = self.startTimer(15000)
		# self.modeTimer = self.startTimer(5000)
		# self.pushTimer = self.startTimer(3000)
		self.show()

	def quit(self):
		self.app.quit()

	def paintEvent(self, event):
		if not self.visible or self.mode == "mouse":
			return

		painter = QtGui.QPainter(self)
		painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		if self.mode == "laser":
			painter.setBrush(self.primaryColor)
		elif self.mode == "highlight":
			painter.setBrush(QtCore.Qt.transparent)
			painter.fillRect(self.app.primaryScreen().geometry(),self.primaryColor)

		painter.drawEllipse(self.point, self.r, self.r)
	
	def timerEvent(self, event):
		if not self.visible:
			return

		if event.timerId() == self.moveTimer:
			# self.point = self.mapFromGlobal(QtGui.QCursor.pos())

			pos = self.ble.readPos()
			x = int(pos[0]*self.app.primaryScreen().geometry().width())
			y = int(pos[1]*self.app.primaryScreen().geometry().height())
			self.point = QtCore.QPoint(x,y)
			QtGui.QCursor.setPos(x,y)

			self.update()

		# elif event.timerId() == self.quitTimer:
		# 	self.quit()

		# elif event.timerId() == self.modeTimer:
		# 	self.changeMode()
		# 	self.update()

		# elif event.timerId() == self.pushTimer:
		# 	pyautogui.press('down')

	def changeVisibility(self, value):
		self.visible = value
		self.update()

	def leftClick(self, value):
		if self.mode == "mouse":
			if value:
				pyautogui.mouseDown()
			else:
				pyautogui.mouseUp()
		else:
			if value:
				pyautogui.keyDown('down')
			else:
				pyautogui.keyUp('down')

	def rightClick(self, value):
		if self.mode == "mouse":
			if value:
				pyautogui.mouseDown(button='right')
			else:
				pyautogui.mouseUp(button='right')
		else:
			if value:
				pyautogui.keyDown('up')
			else:
				pyautogui.keyUp('up')

	def changeMode(self, value):
		if value:
			if self.mode == "laser":
				self.mode = "highlight"

			elif self.mode == "highlight":
				self.mode = "mouse"

			elif self.mode == "mouse":
				self.mode = "laser"

			self.update()


if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	r = 100
	mode = "laser"
	canvas = Canvas(app, r, mode)

	sys.exit(app.exec())