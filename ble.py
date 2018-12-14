from PyQt5 import QtWidgets, QtCore, QtGui, QtBluetooth
import sys

class Ble(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		self.discoverer = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
		self.discoverer.setLowEnergyDiscoveryTimeout(1000)
		self.discoverer.deviceDiscovered.connect(self.checkDevice)
		#self.discoverer.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod.LowEnergyMethod)
		self.discoverer.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod(2))

		self.central = None
		self.show()

	def checkDevice(self, device):
		print('UUID: {UUID}, Name: {name}, rssi: {rssi}'.format(UUID=device.deviceUuid().toString(),name=device.name(),rssi=device.rssi()))
		if device.name() == "Xperia XA1 Ultra":
			print("connecting")
			self.central = QtBluetooth.QLowEnergyController.createCentral(device, self)
			self.central.connected.connect(self.scanServices)
			self.central.disconnected.connect(self.disconnection)
			self.central.discoveryFinished.connect(self.serviceScanDone)
			self.central.error.connect(self.connectError)

			self.central.connectToDevice()

	def scanServices(self):
		self.central.discoverServices()

	def serviceScanDone(self):
		print( self.central.services() )
		self.central.createServiceObject()

	def connectError(self):
		print( self.central.errorString() )

	def disconnection(self):
		print( "peripheral disconnected!" )

if __name__ == '__main__':
	app = QtWidgets.QApplication([])

	ble = Ble()

	sys.exit(app.exec())
