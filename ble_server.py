#!/usr/bin/python

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
import gobject

import random
import struct

from bluez_example import *

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
        self.add_characteristic(ButtonChrc(bus, 1, '00000225-0000-1000-8000-00805f9b34fb', self))
        self.add_characteristic(ButtonChrc(bus, 2, '00000325-0000-1000-8000-00805f9b34fb', self))
        self.add_characteristic(ButtonChrc(bus, 3, '00000425-0000-1000-8000-00805f9b34fb', self))
        self.add_characteristic(ButtonChrc(bus, 4, '00000525-0000-1000-8000-00805f9b34fb', self))

class PositionChrc(Characteristic):
    PB_PS_UUID = '00000125-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.PB_PS_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        
        self.x = 0.5
        self.y = 0.5

        gobject.timeout_add(1000, self.move)

    def notify_motion(self):
        if not self.notifying:
            return
        ba = struct.pack("<ff", self.x, self.y)
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': dbus.ByteArray(ba) }, [])

    def move(self):
        self.x = random.random()
        self.y = random.random()
        # print('Moving to: (' + repr(self.x) + ', ' + repr(self.y) + ')')
        self.notify_motion()
        return True

    def ReadValue(self):
        print('Motion read: (' + repr(self.x) + ', ' + repr(self.y) + ')')
        ba = struct.pack("<ff", self.x, self.y)
        return dbus.ByteArray(ba)

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

class ButtonChrc(Characteristic):
    def __init__(self, bus, index, uuid, service):
        Characteristic.__init__(
                self, bus, index,
                uuid,
                ['read', 'notify'],
                service)
        self.notifying = False
        
        self.state = 0

        gobject.timeout_add(random.randint(1000,5000), self.push)

    def notify_button(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(self.state)] }, [])

    def push(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0
        # print('Push button ' + str(self.state))
        self.notify_button()
        return True

    def ReadValue(self):
        print('Read button ' + str(self.state))
        return [dbus.Byte(self.state)]

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


if __name__ == '__main__':
    main()