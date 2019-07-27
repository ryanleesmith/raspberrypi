import sys

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array

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

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(OBJECT_MANAGER_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

    def registerSuccess(self):
        print('Application registered')

    def registerError(self, error):
        print('Failed to register application: ' + str(error))
        mainloop.quit()

class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(PROPERTY_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]

class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(PROPERTY_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(PROPERTY_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class Descriptor(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(PROPERTY_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

class CharacteristicUserDescriptionDescriptor(Descriptor):
    def __init__(self, bus, index, characteristic):
        #self.writable = 'writable-auxiliaries' in characteristic.flags
        value = array.array('B', b'This is a characteristic for testing')
        self.value = value.tolist()
        Descriptor.__init__(
                self, bus, index,
                '2901',
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        #if not self.writable:
        raise NotPermittedException()
        #self.value = value

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

class SensorApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(SensorService(bus, 0))

class SensorService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, '21f694ed-e0bb-4b50-bc20-753431c8e120', True)
        self.add_characteristic(SensorCharacteristic(bus, 0, self))

class SensorCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                '2ede8dfe-bac3-452b-8e18-f364a2bd267e',
                ['read', 'notify'],
                service)
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 0, self))
        self.notifying = False

    def notify(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(5)] }, [])

    def ReadValue(self, options):
        return [dbus.Byte(10)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

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

    serviceManager = dbus.Interface(bus.get_object(BT_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
    advertisingManager = dbus.Interface(bus.get_object(BT_SERVICE_NAME, adapter), ADVERTISING_MANAGER_IFACE)

    sensorApplication = SensorApplication(bus)
    sensorAdvertisement = SensorAdvertisement(bus, 0)

    mainloop = GObject.MainLoop()

    serviceManager.RegisterApplication(sensorApplication.get_path(), {},
                                        reply_handler=sensorApplication.registerSuccess,
                                        error_handler=sensorApplication.registerError)
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