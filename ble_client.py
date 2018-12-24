from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import sys

class Ble(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		self.discoverer = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
		self.discoverer.setLowEnergyDiscoveryTimeout(10000)
		self.discoverer.deviceDiscovered.connect(self.checkDevice)
		self.discoverer.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

		self.central = None
		self.service1 = None
		self.show()

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
		# self.service1 = self.central.createServiceObject(self.central.services()[0], self.central)
		self.service1 = self.central.createServiceObject(QtBluetooth.QBluetoothUuid('{00003125-0000-1000-8000-00805f9b34fb}'), self.central)
		self.service1.stateChanged.connect(self.discovery)
		self.service1.discoverDetails()
		

	def connectError(self):
		print( self.central.errorString() )

	def disconnection(self):
		print( "peripheral disconnected!" )

	def discovery(self):
		if self.service1.characteristics():
			self.service1.readCharacteristic(self.service1.characteristics()[0])
			print ( self.service1.characteristics()[0].value().size() )
			print ( self.service1.characteristics()[0].value() )
			# print ( ord(self.service1.characteristics()[0].value().at(0)) )

if __name__ == '__main__':
	app = QtWidgets.QApplication([])

	ble = Ble()

	sys.exit(app.exec())
