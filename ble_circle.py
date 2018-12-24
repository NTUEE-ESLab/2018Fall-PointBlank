from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import pyautogui
import random
import sys
import struct

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

		self.moveTimer = self.startTimer(500)
		# self.modeTimer = self.startTimer(5000)
		self.quitTimer = self.startTimer(15000)
		# self.pushTimer = self.startTimer(3000)

		#self.showFullScreen()

		self.discoverer = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
		self.discoverer.setLowEnergyDiscoveryTimeout(10000)
		self.discoverer.deviceDiscovered.connect(self.checkDevice)
		self.discoverer.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

		self.central = None
		self.service1 = None
		self.discoveryDone = False



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
			# self.point = self.mapFromGlobal(QtGui.QCursor.pos())
			# x = random.randint(0, self.app.primaryScreen().geometry().width())
			# y = random.randint(0, self.app.primaryScreen().geometry().height())
			# self.point = QtCore.QPoint(x,y)
			# QtGui.QCursor.setPos(x,y)

			if self.discoveryDone:
				self.service1.readCharacteristic(self.service1.characteristics()[0])
				pos = struct.unpack("<ff", self.service1.characteristics()[0].value())
				x = int(pos[0]*self.app.primaryScreen().geometry().width())
				y = int(pos[1]*self.app.primaryScreen().geometry().height())
				self.point = QtCore.QPoint(x,y)
				QtGui.QCursor.setPos(x,y)

				self.update()

		elif event.timerId() == self.quitTimer:
			self.app.quit()

		elif event.timerId() == self.modeTimer:
			self.changeMode()
			self.update()

		elif event.timerId() == self.pushTimer:
			pyautogui.press('down')

	def changeMode(self):
		if self.mode == "laser":
			self.mode = "highlight"

		elif self.mode == "highlight":
			self.mode = "laser"

	def checkDevice(self, device):
		# print('UUID: {UUID}, Name: {name}, rssi: {rssi}'.format(UUID=device.deviceUuid().toString(),name=device.name(),rssi=device.rssi()))
		if device.name() == "B8-27-EB-FA-20-93":
			print("connecting")
			self.central = QtBluetooth.QLowEnergyController.createCentral(device, self)
			self.central.connected.connect(self.scanServices)
			self.central.disconnected.connect(self.disconnection)
			self.central.discoveryFinished.connect(self.serviceScanDone)
			self.central.error.connect(self.connectError)

			self.central.connectToDevice()

	def scanServices(self):
		print( "connected" )
		self.central.discoverServices()

	def serviceScanDone(self):
		print( self.central.services() )
		self.service1 = self.central.createServiceObject(QtBluetooth.QBluetoothUuid('{00003125-0000-1000-8000-00805f9b34fb}'), self.central)
		self.service1.stateChanged.connect(self.discovery)
		self.service1.discoverDetails()
		
	def connectError(self):
		print( self.central.errorString() )

	def disconnection(self):
		print( "peripheral disconnected!" )

	def discovery(self):
		if self.service1.characteristics():
			self.discoveryDone = True


if __name__ == '__main__':
	app = QtWidgets.QApplication([])
	r = 100
	mode = "laser"
	canvas = Canvas(app, r, mode)

	sys.exit(app.exec())