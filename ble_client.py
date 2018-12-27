from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import sys
import struct

class PointBlankBleClient(QtWidgets.QWidget):

	setupDone = QtCore.pyqtSignal()
	button1 = QtCore.pyqtSignal(bool)
	button2 = QtCore.pyqtSignal(bool)
	button3 = QtCore.pyqtSignal(bool)
	button4 = QtCore.pyqtSignal(bool)

	def __init__(self, parent):
		super().__init__()
		self.parent = parent

		self.discoverer = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
		self.discoverer.setLowEnergyDiscoveryTimeout(0)
		self.discoverer.deviceDiscovered.connect(self.checkDevice)
		self.discoverer.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

		self.central = None
		self.service = None
		self.positionChrc = None
		self.buttonChrcs = []

		self.x = 0.5
		self.y = 0.5

		self.descriptCount = 0

		self.setupDone.connect(parent.start)
		self.button1.connect(parent.changeVisibility)
		self.button2.connect(parent.leftClick)
		self.button3.connect(parent.rightClick)
		self.button4.connect(parent.changeMode)

	def readPos(self):
		# self.service.readCharacteristic(self.positionChrc)
		return self.x, self.y

	def checkDevice(self, device):
		# print('UUID: {UUID}, Name: {name}, rssi: {rssi}'.format(UUID=device.deviceUuid().toString(),name=device.name(),rssi=device.rssi()))
		if device.name() == "B8-27-EB-FA-20-93":
			print("connecting to PointBlank")
			self.central = QtBluetooth.QLowEnergyController.createCentral(device, self)
			self.central.connected.connect(self.scanServices)
			self.central.disconnected.connect(self.disconnection)
			self.central.discoveryFinished.connect(self.servicesScanned)
			self.central.error.connect(self.centralError)

			self.central.connectToDevice()
			self.discoverer.stop()

	def scanServices(self):
		print("connected to PointBlank")
		if self.central != None:
			self.central.discoverServices()

	def servicesScanned(self):
		self.service = self.central.createServiceObject(QtBluetooth.QBluetoothUuid('{00003125-0000-1000-8000-00805f9b34fb}'), self.central)
		self.service.stateChanged.connect(self.detailsDiscovered)
		self.service.descriptorWritten.connect(self.countDescript)
		self.service.discoverDetails()
		
	def centralError(self, e):
		print( self.central.errorString() )
		self.parent.app.quit()

	def disconnection(self):
		print( "PointBlank disconnected!" )
		self.parent.app.quit()

	def detailsDiscovered(self, state):
		if state == QtBluetooth.QLowEnergyService.ServiceDiscovered:
			self.positionChrc = self.service.characteristic(QtBluetooth.QBluetoothUuid('{00000125-0000-1000-8000-00805f9b34fb}'))
			self.buttonChrcs.append(self.service.characteristic(QtBluetooth.QBluetoothUuid('{00000225-0000-1000-8000-00805f9b34fb}')))
			self.buttonChrcs.append(self.service.characteristic(QtBluetooth.QBluetoothUuid('{00000325-0000-1000-8000-00805f9b34fb}')))
			self.buttonChrcs.append(self.service.characteristic(QtBluetooth.QBluetoothUuid('{00000425-0000-1000-8000-00805f9b34fb}')))
			self.buttonChrcs.append(self.service.characteristic(QtBluetooth.QBluetoothUuid('{00000525-0000-1000-8000-00805f9b34fb}')))

			des = self.positionChrc.descriptor( QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.ClientCharacteristicConfiguration) )
			self.service.writeDescriptor(des, bytes.fromhex('0100'))

			for i in range(4):
				des = self.buttonChrcs[i].descriptor( QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.ClientCharacteristicConfiguration) )
				self.service.writeDescriptor(des, bytes.fromhex('0100'))

			pos = self.positionChrc.value()
			self.x, self.y = struct.unpack("<ff", pos)

	def countDescript(self):
		self.descriptCount += 1
		if self.descriptCount == 5:
			self.service.characteristicChanged.connect(self.notification)
			self.setupDone.emit()

	def notification(self, characteristic, value):
		if characteristic == self.positionChrc:
			self.x, self.y = struct.unpack("<ff", value)
		elif characteristic == self.buttonChrcs[0]: #visible
			# print("button 1 visibility")
			self.button1.emit(ord(bytes(value)))
		elif characteristic == self.buttonChrcs[1]: #left click
			# print("button 2 left click")
			self.button2.emit(ord(bytes(value)))
		elif characteristic == self.buttonChrcs[2]: #right click
			# print("button 3 right click")
			self.button3.emit(ord(bytes(value)))
		elif characteristic == self.buttonChrcs[3]: #change mode
			# print("button 4 change mode")
			self.button4.emit(ord(bytes(value)))
