"""
This module handles the current LEDM IO Settings
"""

from enum import Enum


class IOType(Enum):
    """
    The different IO channels
    supported
    """
    LAN = 1
    USB = 2


class HTTP_SCHEMES(Enum):
    """
    The different IO channels
    supported
    """
    HTTP = 1
    HTTPS = 2

HTTPSchemes = {IOType.LAN:"HTTPS://", IOType.USB:"UIO://"}  

IO = IOType.USB 
HTTP_SCHEME = HTTPSchemes[IO]
HTTP_HOST = "USBXXX"



def set_io(host="USBXXX"):
    """
    Sets the LEDM IO Settings

    Args:
        io (str): "LAN" or "USB"
        host (str): If "LAN" then IP address if "USB"
            then portname such as "USB001" for a specific printer
            or "USBXXX" connect to first USB printer device 
    """
    global IO
    global HTTP_SCHEME
    global HTTP_HOST
    IO = IOType.USB
    if not host.upper().startswith("USB"):
        IO = IOType.LAN
    HTTP_SCHEME = HTTPSchemes[IO]
    HTTP_HOST = host

def set_http_scheme(scheme):
    """
    Set HTTP SCHEME to either HTTP or HTTPS
    Args:
        scheme (str): the HTTP Scheme
    """
    global HTTP_SCHEME
    if scheme.upper() not in ["HTTP", "HTTPS"]:
        raise ValueError("HTTP scheme can only be HTTP or HTTPS given {}".format(
            scheme
        ))
    HTTP_SCHEME = scheme.upper() + "://"

