"""
usb device models for the base class UsbDevice and two inherited 
classes ScanUsbDevice and PrinterUsbDevice
"""
# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# Python modules
# =============================================================================
import winreg


# =============================================================================
# local imports
# =============================================================================
from . import util


class UsbDevice(object):
    """
    Information on USB Device
    """
    def __init__(self, guid, device_path, device_instance, properties):
        """
        Initialize UsbDevice specific information
        Args:
            guid (str): Device Class GUID
            device_path (str): Device Instance Path 
            device_instance (int): Device Instance ID
            properties ({str:str}): Device Registry Properties
        
        """
        self._guid = guid
        self._device_path = device_path
        self._device_instance = device_instance
        self._properties = properties
        self._device_id = util.get_device_id(device_instance)
        self._parent_device_instance = util.get_parent(device_instance)
        self._parent_id = util.get_device_id(self._parent_device_instance)
        

    @property
    def class_name(self):
        """
        class name of usb device
        """
        return self._properties.get("SPDRP_CLASS", "UNKNOWN")

    @property
    def description(self):
        """
        description of usb device
        """
        return self._properties.get("SPDRP_DEVICEDESC", "UNKNOWN")

    @property
    def device_id(self):
        """
        This will return the device id 
        """
        return self._device_id
    
    @property
    def device_instance(self):
        """
        This will return the device instance (int)
        """
        return self._device_instance

    @property
    def device_location(self):
        """
        The USB HUB and Port location
        """
        return self._properties.get("SPDRP_LOCATION_INFORMATION", "UNKNOWN")

    @property
    def device_path(self):
        """
        device path of the device
        """
        return self._device_path
    
    @device_path.setter
    def device_path(self, value):
        self._device_path = value

    @property
    def guid(self):
        """
        Device class GUID string for usb device
        """
        return self._guid

    @property
    def hardware_id(self):
        """
        the hardware id for device
        """
        return self._properties.get("SPDRP_HARDWAREID", "UNKNOWN")

    @property
    def parent_device_instance(self):
        """
        parent id of the current device
        """
        return self._parent_device_instance

    @property
    def parent_id(self):
        """
        parent name of the current device
        """
        return self._parent_id

    @property
    def vid(self):
        """
        the VID for device
        """
        return self._properties.get("SPDRP_HARDWAREID", "UNKNOWN")[8:12]

    @property
    def pid(self):
        """
        the VID for device
        """
        return self._properties.get("SPDRP_HARDWAREID", "UNKNOWN")[17:21]

    @property   
    def properties(self):
        """
        returns a dictionary of device properties
        """
        return self._properties

class ScanUsbDevice(UsbDevice):
    """
    Wrapper around Printer USB Device class inherits from UsbDevice
    """
    def __init__(self, guid, device_path, device_instance, properties):
        """
        Initialize PrinterUsbDevice 

        Args:
            guid (str): Device Class GUID
            device_path (str): Device Instance Path 
            device_instance (int): Device Instance ID
            properties ({str:str}): Device Registry Properties
        """
        super().__init__(
            guid=guid,
            device_path=device_path,
            device_instance=device_instance,
            properties=properties)

class PrinterUsbDevice(UsbDevice):
    """
    Wrapper around Printer USB Device class inherits from UsbDevice
    """
    def __init__(self, guid, device_path, device_instance, properties, parent_usb_device, scan_usb_device=None):
        """
        Initialize PrinterUsbDevice 

        Args:
            guid (str): Device Class GUID
            device_path (str): Device Instance Path 
            device_instance (int): Device Instance ID
            properties ({str:str}): Device Registry Properties
            parent_usb_device (UsbDevice): parent of PrinterUsbDevice
            scan_usb_device (ScanUsbDvice): Scan USb device perform LEDM actions
        
        """
        if parent_usb_device is not None:
            properties["SPDRP_LOCATION_INFORMATION"] = parent_usb_device.properties.get("SPDRP_LOCATION_INFORMATION", "UNKNOWN")
        else:
            properties["SPDRP_LOCATION_INFORMATION"] = "UNKOWN"

        super().__init__(
            guid=guid,
            device_path=device_path,
            device_instance=device_instance,
            properties=properties)
        
        #self._guid = guid
        self._parent_usb_device = parent_usb_device
        self._scan_usb_device = scan_usb_device
        self._hub, self._port = util.get_hub_port_name(parent_usb_device)
    
    @property
    def hub(self):
        """
        USB Hub number 
        """
        return self._hub

    @property
    def port(self):
        """
        USB Hub Port number 
        """
        return self._port

    @property
    def parent_usb_device(self):
        """
        Parent UsbDevice 
        """
        return self._parent_usb_device

    @property
    def http_device_path(self):
        """
        Scan UsbDevice 
        """
        return self._scan_usb_device.device_path

    @property
    def scan_usb_device(self):
        """
        Scan UsbDevice 
        """
        return self._scan_usb_device

    @property
    def portname(self):
        """
        USB PortName of active printer device
        """
        if self.device_path == "":
            return ""
    
        update_device_path = "##?#" + self.device_path[4:]
        base_reg_key = r"SYSTEM\CurrentControlSet\Control\DeviceClasses\\" + self.guid + "\\" + \
            update_device_path + "\\#\\Device Parameters"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_reg_key) as key: 
            base_name, _ = winreg.QueryValueEx(key, 'Base Name')
            port_number, _ = winreg.QueryValueEx(key, 'Port Number')
            return base_name + str(port_number).zfill(3)