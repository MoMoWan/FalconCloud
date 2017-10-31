"""
Interface with USB Devices 
"""

from .api import get_printers, is_printer_detected, get_scan_devices 
from .api import get_usb_devices, wait_for_printer_connected, wait_printer_not_connected
from .setupapi import GUID_DEVINTERFACE_SCAN_DEVICE, GUID_DEVINTERFACE_USB_PRINT, GUID_DEVINTERFACE_USB_DEVICE


__title__ = "usb_device"
__version__ = '$Revision: 56797 $ '
__author__ = '$Author: lclampitt $ '
__date__ = '$Date: 2017-08-01 04:51:11 +0800 (Tue, 01 Aug 2017) $ '


