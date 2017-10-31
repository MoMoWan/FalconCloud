"""
Utility methods for USB devices

"""

import logging
import binascii
import ctypes
from ctypes.wintypes import DWORD, WCHAR

from . import setupapi

log = logging.getLogger(__name__)


def guid_str_to_structure(guid):
    """
    Convert guid str in format {28d78fad-5a12-11d1-ae5b-0000f803a8c2} into
    Guid structure

    Args:
        guid (str): guid in str format {28d78fad-5a12-11d1-ae5b-0000f803a8c2}

    Returns:
        setupapi.Guid: GUID ctypes structure
    """
    # check if this is already a GUID structure
    if isinstance(guid, setupapi.GUID):
        return guid

    # convert string to GUID structure
    raw_guid = ''.join(guid.strip("{}").split('-'))
    if len(raw_guid) != 32:
        raise SyntaxError("{} incorrect format".format(guid))

    d1 = int(raw_guid[0:8], 16)
    d2 = int(raw_guid[8:12], 16)
    d3 = int(raw_guid[12:16], 16)
    d4 = (ctypes.c_ubyte * 8).from_buffer_copy(bytes.fromhex(raw_guid[16:]))
    guid_structure = type(setupapi.GUID_DEVINTERFACE_USB_PRINT)(d1, d2, d3, d4)
    return guid_structure


def guid_structure_to_str(guid):
    """
    convert guid ctypes structure to string format
    Args:
        guid (setupapi.Guid): Guid structure

    Returns:
        str: guid str format
    """
    # check if it is a str already
    if isinstance(guid, str):
        return guid

    return "{%08x-%04x-%04x-%s-%s}" % (
        guid.Data1,
        guid.Data2,
        guid.Data3,
        ''.join(["%02x" % d for d in guid.Data4[:2]]),
        ''.join(["%02x" % d for d in guid.Data4[2:]]))


def get_parent_usb_device(device_instance, usb_low_Level_devices):
    """
    Get parent device based device_instance searching
    usb_low_Level_devices for a match

    Args:
        device_instance (int): The Device Instance ID
        usb_low_Level_devices ([UsbDevices]): a list of usb devices

    Returns:
        UsbDevice: found parent usb device
    """
    parent_id = get_parent(device_instance)
    parent_name = get_device_id(parent_id)
    unique_instance_id = parent_name.split("\\", 2)[-1]
    usb_layer = None
    for usb_device in usb_low_Level_devices:
        temp_device_path = usb_device.device_path
        if not isinstance(temp_device_path, str):
            temp_device_path = temp_device_path.decode('utf-8')
        if unique_instance_id.lower() in temp_device_path.lower():
            usb_layer = usb_device
    return usb_layer


def get_class_dev_handle(guid, flags):
    """
    Get Device class handle for a given guid
    Args:
        guid (str|setupapi.GUID): Guid of Device class
        flags (int): variable that specifies control options

    Returns:
        HDEVINFO: device class handle
    """
    guid_struct = guid_str_to_structure(guid)
    handle_to_device_info_class = setupapi.SetupDiGetClassDevs(ctypes.byref(
        guid_struct), None, setupapi.NULL, flags)
    return handle_to_device_info_class


def get_device_interface_data(handle_to_device_info_class, interface_index, guid):
    """
    Get the Device Interface Data based on the interface_index. If the ERROR_NO_MORE_ITEMS
    is returned for given index None is returned.

    Args:
        handle_to_device_info_class (HDEVINFO): handle to device class
        interface_index (int): interface Index
        guid (str|GUID): The device class guid

    Returns:
        SP_DEVICE_INTERFACE_DATA | None: The device information data for interface_index if
            ERROR_NO_MORE_ITEMS is reached None is returned.

    Raises:
        WinError: if a different error other than  ERROR_NO_MORE_ITEMS

    """
    guid_struct = guid_str_to_structure(guid)
    device_interface_data = setupapi.SP_DEVICE_INTERFACE_DATA()
    device_interface_data.cbSize = ctypes.sizeof(device_interface_data)
    if not setupapi.SetupDiEnumDeviceInterfaces(
            handle_to_device_info_class,
            None,
            ctypes.byref(guid_struct),
            interface_index,
            ctypes.byref(device_interface_data)
    ):
        if ctypes.GetLastError() != setupapi.ERROR_NO_MORE_ITEMS:
            raise ctypes.WinError()
        return None
    return device_interface_data


def get_parent(device_instance):
    """
    This returns the parent device instance id
    Args:
        device_instance (int): The device instance id

    Returns:
        int: the parent device id

    """
    parent = ctypes.wintypes.DWORD(0)
    setupapi.CM_Get_Parent(ctypes.byref(parent), device_instance, 0)
    return parent.value


def get_device_id(device_instance):
    """
    This return the device instance id based from the device instance
    on a local machine.

    Args:
        device_instance (int): The device instance id

    Returns:
        str: the device instance id string

    """
    buffer = ctypes.create_unicode_buffer(255)
    setupapi.CM_Get_Device_ID(device_instance, ctypes.byref(buffer), 255, 0)
    return buffer.value


def get_setupdi_device_interface_detail(handle_to_device_info_class, dev_interface_info_data):
    """
    This gets the device interface detial

    Args:
        handle_to_device_info_class (HDEVINFO): handle to device class
        dev_interface_info_data (SP_DEVICE_INTERFACE_DATA): Device Interface Class data

    Returns:
        (PSP_DEVICE_INTERFACE_DETAIL_DATA, SP_DEVINFO_DATA): Tuple of device datail daata and
            Dev info data
    """
    # get the size of the buffer
    dwNeeded = DWORD()
    if not setupapi.SetupDiGetDeviceInterfaceDetail(
            handle_to_device_info_class,
            ctypes.byref(dev_interface_info_data),
            None, 0, ctypes.byref(dwNeeded),
            None
    ):
        # Ignore ERROR_INSUFFICIENT_BUFFER
        if ctypes.GetLastError() != setupapi.ERROR_INSUFFICIENT_BUFFER:
            raise ctypes.WinError()

    # create inner class with the buffer size
    class SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
        """ local class to in order to allocate buffer """
        _fields_ = [
            ('cbSize', DWORD),
            ('DevicePath', WCHAR * (dwNeeded.value - ctypes.sizeof(DWORD))),
        ]

        def __str__(self):
            return "DevicePath:%s" % (self.DevicePath)

    # call again with the correct information
    device_interface_detail_data = SP_DEVICE_INTERFACE_DETAIL_DATA_W()
    device_interface_detail_data.cbSize = setupapi.SIZEOF_SP_DEVICE_INTERFACE_DETAIL_DATA_W
    devinfo_data = setupapi.SP_DEVINFO_DATA()
    devinfo_data.cbSize = ctypes.sizeof(devinfo_data)
    if not setupapi.SetupDiGetDeviceInterfaceDetail(
            handle_to_device_info_class,
            ctypes.byref(dev_interface_info_data),
            ctypes.byref(device_interface_detail_data), dwNeeded, None,
            ctypes.byref(devinfo_data)
    ):
        raise ctypes.WinError()

    return device_interface_detail_data, devinfo_data


def get_device_properties(handle_to_device_info_class, dev_info_data):
    """
    This returs the dictionary of the Device Registry properties. It will
    interate to get the friendly values.

    Args:
        handle_to_device_info_class (HDEVINFO): handle to device class
        dev_info_data (SP_DEVINFO_DATA): Device information data structure

    Returns:
        {str: str} : dictionary of registry property names and values

    """
    reg_keys = {}
    sprdp_data_type = DWORD(-1)
    buffer_size = DWORD(-1)
    for spdrp_reg_prop in setupapi.SPDRP_PROPERTIES_DICT:
        szFriendlyName = ctypes.create_unicode_buffer(1024)
        if setupapi.SetupDiGetDeviceRegistryProperty(
                handle_to_device_info_class,
                ctypes.byref(dev_info_data),
                spdrp_reg_prop,
                ctypes.byref(sprdp_data_type),
                ctypes.byref(szFriendlyName), ctypes.sizeof(szFriendlyName) - 1,
                ctypes.byref(buffer_size)
        ):
            if sprdp_data_type.value in (1, 7):
                reg_keys[setupapi.SPDRP_PROPERTIES_DICT[spdrp_reg_prop]] = szFriendlyName.value
            elif sprdp_data_type.value == 4:
                reg_keys[setupapi.SPDRP_PROPERTIES_DICT[spdrp_reg_prop]] = \
                    binascii.hexlify(szFriendlyName.value.encode()).decode('utf-8').upper()
        else:
            reg_keys[setupapi.SPDRP_PROPERTIES_DICT[spdrp_reg_prop]] = ""

    return reg_keys


def get_hub_port_name(usb_comp_device):
    """
    It will return HUB and Port strings from a USB composite device

    Args:
        usb_comp_device (UsbDevice): The usb composite device

    Returns:
        (str, str): Hub, Port information
    """
    hub = ""
    port = ""
    if usb_comp_device:
        try:
            hub_port_combo = usb_comp_device.properties["SPDRP_LOCATION_INFORMATION"]
            if "." in hub_port_combo:
                tport, thub = hub_port_combo.split(".")
                hub = thub.split("#")[-1]
                port = tport.split("#")[-1]
        except AttributeError:
            pass

    return hub, port


def get_setupdi_device_interface_details(guid, flags=setupapi.DIGCF_DEVICEINTERFACE|setupapi.DIGCF_PRESENT):
    """
    Generator to loop thru device class detail yielding handle to the device class, device interface data,
    and device information data

    Args:
        guid (str|GUID): The device class guid
        flags (int): The control flag that controls the type of devices to check for examples are
            setupapi.DIGCF_DEVICEINTERFACE and setupapi.DIGCF_PRESENT

    Returns:
        (HDEVINFO, SP_DEVICE_INTERFACE_DETAIL_DATA_A, SP_DEVINFO_DATA): yields tuple information
    """

    guid_struct = guid_str_to_structure(guid)
    handle_to_device_info_class = get_class_dev_handle(guid_struct, flags)
    try:
        for device_index in range(256):
            dev_interface_info_data = get_device_interface_data(handle_to_device_info_class, device_index, guid_struct)
            if dev_interface_info_data is None:
                break
            device_interface_data, dev_info_data = get_setupdi_device_interface_detail(handle_to_device_info_class, dev_interface_info_data)
            yield handle_to_device_info_class, device_interface_data, dev_info_data
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(handle_to_device_info_class)
