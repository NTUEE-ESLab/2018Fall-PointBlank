#!/usr/bin/python

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
import gobject

import random
import struct
import os
import time
import errno
import subprocess

import serial

from bluez_example import *

read_path = "/tmp/server_in.pipe"
write_path = "/tmp/server_out.pipe"
rf = None
wf = None

start_time = None



mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

GATT_MANAGER_IFACE = 'org.bluez.GattManager1'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

class PointBlankAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid('3125')
        self.add_local_name('PointBlank')
        self.include_tx_power = True

class PointBlankService(Service):
    PB_UUID = '00003125-0000-1000-8000-00805f9b34fb'
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.PB_UUID, True)
        self.add_characteristic(PositionChrc(bus, 0, self))
        self.add_characteristic(ButtonsPressChrc(bus, 1, '00000225-0000-1000-8000-00805f9b34fb', self))

class PositionChrc(Characteristic):
    PB_PS_UUID = '00000125-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.PB_PS_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        
        # self.x = 0.5
        # self.y = 0.5

        self.ba = b"\0\0\0\0\0\0\0\0"
        gobject.timeout_add(10, self.move)

    def notify_motion(self):
        if not self.notifying:
            return
        # ba = struct.pack("<ff", self.x, self.y)
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': dbus.ByteArray(self.ba) }, [])

    def move(self):
        global rf
        try:
            b = os.read(rf, 8)
            if b:
                self.ba = b
                self.notify_motion()
        except OSError as err:
            pass

        return True

    def ReadValue(self):
        return dbus.ByteArray(self.ba)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_motion()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

class ButtonsPressChrc(Characteristic):
    def __init__(self, bus, index, uuid, service):
        Characteristic.__init__(
                self, bus, index,
                uuid,
                ['read', 'notify'],
                service)
        self.notifying = False
        
        self.state = 0
        self.prevState = 0
        self.action = 0
        self.serialPort = serial.Serial("/dev/ttyACM0", 9600, timeout = 0)
        self.serialPort.flushInput()

        gobject.timeout_add(50, self.read_button)

    def notify_button(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(self.action)] }, [])

    def read_button(self):
        global rf
        global wf
        global start_time

        send = True

        b = self.serialPort.read()
        if b:
            self.state = ord(b)
            if self.state != self.prevState:
                if self.state == 0:
                    self.action = self.prevState*2 - 1
                    if self.prevState == 4:
                        os.write(wf, bytearray(b'\x00'))
                    elif self.prevState == 5:
                        if time.time() - start_time > 2:
                            os.write(wf, bytearray(b'\xFF'))
                            os.close(rf)
                            os.close(wf)


                            mainloop.quit()
                        else:
                            send = False

                    # print ("button released")

                else:
                    self.action = self.state*2
                    if self.state == 4:
                        os.write(wf, bytearray(b'\x01'))
                    if self.state == 5:
                        start_time = time.time()
                    # print ("button pushed")

            self.prevState = self.state

            if send:
                self.notify_button()

        return True

    def ReadValue(self):
        print('Action ' + str(self.action))
        return [dbus.Byte(self.action)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_button()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

def register_service_cb():
    print('GATT service registered')


def register_service_error_cb(error):
    print('Failed to register service: ' + str(error))
    mainloop.quit()

def register_ad_cb():
    print 'Advertisement registered'


def register_ad_error_cb(error):
    print 'Failed to register advertisement: ' + str(error)
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.iteritems():
        if LE_ADVERTISING_MANAGER_IFACE in props:
            return o

    return None

def main():
    global mainloop
    global rf
    global wf

    rf = os.open( read_path, os.O_RDONLY |  os.O_NONBLOCK )
    wf = os.open( write_path, os.O_WRONLY )

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print 'LEAdvertisingManager1 interface not found'
        return

    adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                   "org.freedesktop.DBus.Properties");

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    pb_service = PointBlankService(bus, 0)

    pb_advertisement = PointBlankAdvertisement(bus, 0)

    mainloop = gobject.MainLoop()

    ad_manager.RegisterAdvertisement(pb_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    service_manager.RegisterService(pb_service.get_path(), {},
                                    reply_handler=register_service_cb,
                                    error_handler=register_service_error_cb)

    mainloop.run()

    # subprocess.call(["shutdown", "-h", "now"])


if __name__ == '__main__':
    main()