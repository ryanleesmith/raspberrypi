import sys

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from gi.repository import GObject

BT_SERVICE_NAME             = 'org.bluez'
ADVERTISING_MANAGER_IFACE   = 'org.bluez.LEAdvertisingManager1'
ADVERTISEMENT_IFACE         = 'org.bluez.LEAdvertisement1'
GATT_MANAGER_IFACE          = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE          = 'org.bluez.GattService1'
GATT_CHRC_IFACE             = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE             = 'org.bluez.GattDescriptor1'
OBJECT_MANAGER_IFACE        = 'org.freedesktop.DBus.ObjectManager'
PROPERTY_IFACE              = 'org.freedesktop.DBus.Properties'

mainloop = None

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.type = type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = None
        self.include_tx_power = None
        self.data = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.type

        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids, signature='s')

        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids, signature='s')

        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(self.manufacturer_data, signature='qv')

        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data, signature='sv')

        if self.local_name is not None:
            properties['LocalName'] = dbus.String(self.local_name)

        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)

        if self.data is not None:
            properties['Data'] = dbus.Dictionary(self.data, signature='yv')

        return {ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    def add_local_name(self, name):
        self.local_name = dbus.String(name)

    def add_data(self, type, data):
        if not self.data:
            self.data = dbus.Dictionary({}, signature='yv')
        self.data[type] = dbus.Array(data, signature='y')

    @dbus.service.method(PROPERTY_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[ADVERTISEMENT_IFACE]

    @dbus.service.method(ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('%s: Released!' % self.path)

    def registerSuccess(self):
        print('Advertisement registered')

    def registerError(self, error):
        print('Failed to register advertisement: ' + str(error))
        mainloop.quit()

class SensorAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_local_name('SensorAdvertisement')
        self.include_tx_power = True

def findAdapter(bus):
    objManager = dbus.Interface(bus.get_object(BT_SERVICE_NAME, '/'), OBJECT_MANAGER_IFACE)
    objects = objManager.GetManagedObjects()

    adapter = None
    for object, props in objects.items():
        if ADVERTISING_MANAGER_IFACE in props:
            adapter = object
            break

    if adapter:
        adapterProps = dbus.Interface(bus.get_object(BT_SERVICE_NAME, adapter), PROPERTY_IFACE)
        adapterProps.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    return adapter

def init():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    adapter = findAdapter(bus)

    if not adapter:
        print('Advertising Manager interface not found')
        return

    advertisingManager = dbus.Interface(bus.get_object(BT_SERVICE_NAME, adapter), ADVERTISING_MANAGER_IFACE)

    sensorAdvertisement = SensorAdvertisement(bus, 0)

    mainloop = GObject.MainLoop()

    advertisingManager.RegisterAdvertisement(sensorAdvertisement.get_path(), {},
                                     reply_handler=sensorAdvertisement.registerSuccess,
                                     error_handler=sensorAdvertisement.registerError)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        #sensorAdvertisement.Release()
        advertisingManager.UnregisterAdvertisement(sensorAdvertisement)
        dbus.service.Object.remove_from_connection(sensorAdvertisement)

if __name__ == '__main__':
    init()