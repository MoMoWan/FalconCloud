"""
This contains methods exposed to the user.

"""

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# Standard Python modules
# =============================================================================
import time

# =============================================================================
# local imports
# =============================================================================
from . import models
from . import setupapi
from .setupapi import GUID_DEVINTERFACE_USB_PRINT
from .setupapi import GUID_DEVINTERFACE_USB_DEVICE
from .setupapi import GUID_DEVINTERFACE_SCAN_DEVICE
from . import util

def get_printers(available_only=True):
    """
    It will return a list of printer usb devices
    Args:
        available_only (bool): to detect conected devices

    Returns:
        [PrinterUsbDevice]: list of Printer Usb Devices
    """

    usb_low_Level_devices = get_usb_devices(guid=GUID_DEVINTERFACE_USB_DEVICE, available_only=available_only)
    scan_devices = get_scan_devices(available_only=True)

    flags = setupapi.DIGCF_DEVICEINTERFACE
    if available_only:
        flags |= setupapi.DIGCF_PRESENT
    printer_usb_devices = []
    for g_hdi, idd, devinfo in util.get_setupdi_device_interface_details(GUID_DEVINTERFACE_USB_PRINT, flags):

        prop_keys = util.get_device_properties(g_hdi, devinfo)
        if prop_keys is None:
            prop_keys = {}
        parent_usb_device = util.get_parent_usb_device(devinfo.DevInst, usb_low_Level_devices)
        find_first_scan_device = next(
            (i for i in scan_devices if i.parent_id == parent_usb_device.device_id),
            None)

        printer_usb_device = models.PrinterUsbDevice(
            guid=util.guid_structure_to_str(GUID_DEVINTERFACE_USB_PRINT),
            device_path=idd.DevicePath,
            device_instance=devinfo.DevInst,
            properties=prop_keys,
            parent_usb_device=parent_usb_device,
            scan_usb_device=find_first_scan_device
            )
        printer_usb_devices.append(printer_usb_device)

    return printer_usb_devices


def get_usb_devices(guid=GUID_DEVINTERFACE_USB_DEVICE, available_only=True):
    """
    It will return a list of usb devices based on device class guid
    Args:
        available_only (bool): to detect conected devices

    Returns:
        [UsbDevice]: list of Usb Devices
    """
    flags = setupapi.DIGCF_DEVICEINTERFACE
    if available_only:
        flags |= setupapi.DIGCF_PRESENT
    usb_devices = []
    for g_hdi, idd, devinfo in util.get_setupdi_device_interface_details(guid, flags):

        # Get Properties information on device
        prop_keys = util.get_device_properties(g_hdi, devinfo)

        # create UsbDevice
        usb_device = models.UsbDevice(
            guid=util.guid_structure_to_str(guid),
            device_path=idd.DevicePath,
            device_instance=devinfo.DevInst,
            properties=prop_keys
            )
        usb_devices.append(usb_device)

    return usb_devices


def get_scan_devices(available_only=True):
    """
    It will return a list of scan specific usb device
    Args:
        available_only (bool): to detect conected devices

    Returns:
        [UsbDevice]: list of Usb Devices
    """
    flags = setupapi.DIGCF_DEVICEINTERFACE
    if available_only:
        flags |= setupapi.DIGCF_PRESENT
    scan_usb_devices = []
    guid = GUID_DEVINTERFACE_SCAN_DEVICE
    for g_hdi, idd, devinfo in util.get_setupdi_device_interface_details(guid, flags):

        # Get Properties information on device
        prop_keys = util.get_device_properties(g_hdi, devinfo)
        # create UsbDevice
        scan_usb_device = models.ScanUsbDevice(
            guid=util.guid_structure_to_str(guid),
            device_path=idd.DevicePath,
            device_instance=devinfo.DevInst,
            properties=prop_keys
            )
        scan_usb_devices.append(scan_usb_device)

    return scan_usb_devices



def is_printer_detected():
    """
    determines if a printer is detected

    Args:

    Returns:
        bool: True if printer connected else False
            not conntected.
    """
    try:
        for _ in get_printers():
            return True
    except Exception as ex:
        log.debug(str(ex))
        pass
    return False

def wait_for_printer_connected(time_to_wait, loop_delay=.5):
    """
    This will wait time_to_wait seconds for a printer to
    be connected. If it does not detect printer within
    that time it will raise IOError

    Args:
        time_to_wait (int): The time to wait

    Returns:
        [PrinterUsbDevice]: It will return list of printers


    """
    log.info("Waiting for printer to be connected")
    start = time.time()
    while (time.time() - start) < int(time_to_wait):
        connected = is_printer_detected()
        log.debug("usb connected = {}".format(connected))
        if connected:
            return get_printers()

        current_time = int(time.time() - start)
        log.info(
            "Waiting for printer to be detected: " +
            str(current_time) +
            " of " +
            str(time_to_wait))
        time.sleep(loop_delay)

    raise IOError("Printer not connected")

def wait_printer_not_connected(time_to_wait, loop_delay=.5):
    """
    This will wait time_to_wait seconds for printer
    not to be connected to system. If the printer is
    still detected within after that time it will
    raise an IO Error

    Args:
        time_to_wait (int): The time to wait
        loop_delay (float): The time to sleep between loops

    Returns:

    Raises:
        IOError: if pritner is still detected after
            time_to_wait seconds
    """

    start = time.time()
    while (time.time() - start) < int(time_to_wait):
        connected = is_printer_detected()
        log.debug("usb connected = {}".format(connected))
        if not connected:
            return

        current_time = int(time.time() - start)
        log.info(
            "Waiting for printer to disconnect: " +
            str(current_time) +
            " of " +
            str(time_to_wait))
        time.sleep(loop_delay)

    raise IOError("Printer is still connected")