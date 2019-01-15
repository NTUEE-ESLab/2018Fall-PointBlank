#!/usr/bin/python
from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import pyautogui
import random
import sys
import os
import json
import time

import ble_client

class Canvas(QtWidgets.QWidget):
	def __init__(self, app):
		super().__init__()
		self.readSettings()

		self.setGeometry(app.primaryScreen().geometry())
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)		
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.FramelessWindowHint | QtCore.Qt.X11BypassWindowManagerHint)

		self.app = app
		self.point = app.primaryScreen().geometry().center()

		self.ble = ble_client.PointBlankBleClient(self)

	def readSettings(self):

		try:
			self.fd = os.open("settings.dat", os.O_RDONLY)
			buf = os.read(self.fd, 256)
			args = json.loads(buf.decode())
			self.r = args[0]
			self.width = args[1]
			self.color = QtGui.QColor(args[2][0],args[2][1],args[2][2],args[2][3])
			self.factor = args[3]
			os.close(self.fd)
		except:
			self.r = 100
			self.width = 5
			self.color = QtGui.QColor(100,100,100,200)
			self.factor = 2

	def start(self):
		self.mode = "started"
		self.visible = True
		self.show()
		self.repaint()

	def quit(self):
		self.mode = "quitting"
		self.visible = True
		self.repaint()
		time.sleep(5)
		self.app.quit()

	def paintEvent(self, event):
		if not self.visible or self.mode == "mouse":
			return

		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		if self.mode == "laser":
			pen = QtGui.QPen(self.color)
			pen.setWidth(self.width)
			painter.setPen(pen)
			painter.drawEllipse(self.point, self.r, self.r)
		elif self.mode == "highlight":
			painter.fillRect(self.app.primaryScreen().geometry(),self.color)
			painter.setBrush(QtCore.Qt.transparent)
			painter.drawEllipse(self.point, self.r, self.r)
		elif self.mode == "magnify":
			painter.setClipRegion(QtGui.QRegion((self.point.x() - self.r), (self.point.y() - self.r), 2*self.r, 2*self.r, QtGui.QRegion.Ellipse))
			painter.setClipping(True)
			painter.translate(-(self.factor - 1)*self.point)
			painter.drawPixmap(0, 0, self.screenshot)
			painter.setClipping(False)
			pen = QtGui.QPen(self.color)
			pen.setWidth(self.width)
			painter.setPen(pen)
			painter.drawEllipse(self.point*self.factor, self.r, self.r)
		else:
			font = QtGui.QFont()
			font.setPixelSize(16)
			painter.setFont(font)
			if self.mode == "started":
				boundingRect = painter.boundingRect(QtCore.QRectF(self.app.primaryScreen().geometry()), QtCore.Qt.AlignRight|QtCore.Qt.AlignTop, "Connected to PointBlank")
				painter.fillRect(boundingRect, QtGui.QColor(255,255,255,100))
				painter.drawText(QtCore.QRectF(self.app.primaryScreen().geometry()), QtCore.Qt.AlignRight|QtCore.Qt.AlignTop, "Connected to PointBlank")
				self.mode = "laser"
				self.visible = False

			elif self.mode == "quitting":
				boundingRect = painter.boundingRect(QtCore.QRectF(self.app.primaryScreen().geometry()), QtCore.Qt.AlignRight|QtCore.Qt.AlignTop, "PointBlank has disconnected")
				painter.fillRect(boundingRect, QtGui.QColor(255,255,255,100))
				painter.drawText(QtCore.QRectF(self.app.primaryScreen().geometry()), QtCore.Qt.AlignRight|QtCore.Qt.AlignTop, "PointBlank has disconnected")

	def move(self):
		if not self.visible:
			return

		pos = self.ble.readPos()
		x = int(pos[0]*self.app.primaryScreen().geometry().width())
		y = int(pos[1]*self.app.primaryScreen().geometry().height())
		self.point = QtCore.QPoint(x,y)
		QtGui.QCursor.setPos(x,y)

		self.update()

	def changeVisibility(self, value):
		self.visible = value
		if self.mode == "magnify" and value:
			sc = self.app.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
			self.screenshot = sc.scaled(self.factor*sc.size())
		pos = self.ble.readPos()
		x = int(pos[0]*self.app.primaryScreen().geometry().width())
		y = int(pos[1]*self.app.primaryScreen().geometry().height())
		self.point = QtCore.QPoint(x,y)
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
				self.mode = "magnify"

			elif self.mode == "magnify":
				self.mode = "mouse"

			elif self.mode == "mouse":
				self.mode = "laser"

			self.update()


if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	canvas = Canvas(app)

	sys.exit(app.exec())