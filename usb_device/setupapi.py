"""
This is leverage from scanwin32.py it basically it is 
a wrapper around the win32 setupapi 

"""

import logging
import ctypes
log = logging.getLogger(__name__)


NULL = 0
HDEVINFO = ctypes.c_int
BOOL = ctypes.c_int
CHAR = ctypes.c_char
WCHAR = ctypes.c_wchar
PCTSTR = ctypes.c_char_p
HWND = ctypes.c_uint
DWORD = ctypes.c_ulong
PDWORD = ctypes.POINTER(DWORD)
ULONG = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(ULONG)
PBYTE = ctypes.c_void_p
DIGCF_PRESENT = 2
DIGCF_DEVICEINTERFACE = 16
INVALID_HANDLE_VALUE = 0

ERROR_SUCCESS = 0
ERROR_INVALID_DATA = 13
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_NO_MORE_ITEMS = 259

SPDRP_DEVICEDESC = 0x00000000
SPDRP_HARDWAREID = 0x00000001
SPDRP_COMPATIBLEIDS = 0x00000002
SPDRP_UNUSED0 = 0x00000003
SPDRP_SERVICE = 0x00000004
SPDRP_UNUSED1 = 0x00000005
SPDRP_UNUSED2 = 0x00000006
SPDRP_CLASS = 0x00000007
SPDRP_CLASSGUID = 0x00000008
SPDRP_DRIVER = 0x00000009
SPDRP_CONFIGFLAGS = 0x0000000A
SPDRP_MFG = 0x0000000B
SPDRP_FRIENDLYNAME = 0x0000000C
SPDRP_LOCATION_INFORMATION = 0x0000000D
SPDRP_PHYSICAL_DEVICE_OBJECT_NAME = 0x0000000E
SPDRP_CAPABILITIES = 0x0000000F
SPDRP_UI_NUMBER = 0x00000010
SPDRP_UPPERFILTERS = 0x00000011
SPDRP_LOWERFILTERS = 0x00000012
SPDRP_BUSTYPEGUID = 0x00000013
SPDRP_LEGACYBUSTYPE = 0x00000014
SPDRP_BUSNUMBER = 0x00000015
SPDRP_ENUMERATOR_NAME = 0x00000016
SPDRP_SECURITY = 0x00000017
SPDRP_SECURITY_SDS = 0x00000018
SPDRP_DEVTYPE = 0x00000019
SPDRP_EXCLUSIVE = 0x0000001A
SPDRP_CHARACTERISTICS = 0x0000001B
SPDRP_ADDRESS = 0x0000001C
SPDRP_UI_NUMBER_DESC_FORMAT = 0X0000001D
SPDRP_DEVICE_POWER_DATA = 0x0000001E
SPDRP_REMOVAL_POLICY = 0x0000001F
SPDRP_REMOVAL_POLICY_HW_DEFAULT = 0x00000020
SPDRP_REMOVAL_POLICY_OVERRIDE = 0x00000021
SPDRP_INSTALL_STATE = 0x00000022
SPDRP_LOCATION_PATHS = 0x00000023
SPDRP_BASE_CONTAINERID = 0x00000024
SPDRP_MAXIMUM_PROPERTY = 0x00000025

SPDRP_PROPERTIES_DICT = {
    0x00000000: "SPDRP_DEVICEDESC",
    0x00000001: "SPDRP_HARDWAREID",
    0x00000002: "SPDRP_COMPATIBLEIDS",
    0x00000003: "SPDRP_UNUSED0",
    0x00000004: "SPDRP_SERVICE",
    0x00000005: "SPDRP_UNUSED1",
    0x00000006: "SPDRP_UNUSED2",
    0x00000007: "SPDRP_CLASS",
    0x00000008: "SPDRP_CLASSGUID",
    0x00000009: "SPDRP_DRIVER",
    0x0000000A: "SPDRP_CONFIGFLAGS",
    0x0000000B: "SPDRP_MFG",
    0x0000000C: "SPDRP_FRIENDLYNAME",
    0x0000000D: "SPDRP_LOCATION_INFORMATION",
    0x0000000E: "SPDRP_PHYSICAL_DEVICE_OBJECT_NAME",
    0x0000000F: "SPDRP_CAPABILITIES",
    0x00000010: "SPDRP_UI_NUMBER",
    0x00000011: "SPDRP_UPPERFILTERS",
    0x00000012: "SPDRP_LOWERFILTERS",
    0x00000013: "SPDRP_BUSTYPEGUID",
    0x00000014: "SPDRP_LEGACYBUSTYPE",
    0x00000015: "SPDRP_BUSNUMBER",
    0x00000016: "SPDRP_ENUMERATOR_NAME",
    0x00000017: "SPDRP_SECURITY",
    0x00000018: "SPDRP_SECURITY_SDS",
    0x00000019: "SPDRP_DEVTYPE",
    0x0000001A: "SPDRP_EXCLUSIVE",
    0x0000001B: "SPDRP_CHARACTERISTICS",
    0x0000001C: "SPDRP_ADDRESS",
    0X0000001D: "SPDRP_UI_NUMBER_DESC_FORMAT",
    0x0000001E: "SPDRP_DEVICE_POWER_DATA",
    0x0000001F: "SPDRP_REMOVAL_POLICY",
    0x00000020: "SPDRP_REMOVAL_POLICY_HW_DEFAULT",
    0x00000021: "SPDRP_REMOVAL_POLICY_OVERRIDE", 
    0x00000022: "SPDRP_INSTALL_STATE",
    0x00000023: "SPDRP_LOCATION_PATHS",
    0x00000024: "SPDRP_BASE_CONTAINERID"
}


def ValidHandle(value):
    """
    This is used signarure as the return type for 
    SetupDiGetClassDevs
    """
    if value == 0:
        raise ctypes.WinError()
    return value


class GUID(ctypes.Structure):
    """
    typedef struct _GUID {
    DWORD Data1;
    WORD  Data2;
    WORD  Data3;
    BYTE  Data4[8];
    } GUID;
    """
    _fields_ = [
        ('Data1', ctypes.c_ulong),
        ('Data2', ctypes.c_ushort),
        ('Data3', ctypes.c_ushort),
        ('Data4', ctypes.c_ubyte * 8),
    ]

    def __str__(self):
        return "{%08x-%04x-%04x-%s-%s}" % (
            self.Data1,
            self.Data2,
            self.Data3,
            ''.join(["%02x" % d for d in self.Data4[:2]]),
            ''.join(["%02x" % d for d in self.Data4[2:]]),
        )


class SP_DEVINFO_DATA(ctypes.Structure):
    """
    typedef struct _SP_DEVINFO_DATA {
    DWORD     cbSize;
    GUID      ClassGuid;
    DWORD     DevInst;
    ULONG_PTR Reserved;
    } SP_DEVINFO_DATA, *PSP_DEVINFO_DATA;
    """
    _fields_ = [
        ('cbSize', DWORD),
        ('ClassGuid', GUID),
        ('DevInst', DWORD),
        ('Reserved', ULONG_PTR),
    ]

    def __str__(self):
        return "ClassGuid:%s DevInst:%s" % (self.ClassGuid, self.DevInst)


PSP_DEVINFO_DATA = ctypes.POINTER(SP_DEVINFO_DATA)


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    """
    typedef struct _SP_DEVICE_INTERFACE_DATA {
    DWORD     cbSize;
    GUID      InterfaceClassGuid;
    DWORD     Flags;
    ULONG_PTR Reserved;
    } SP_DEVICE_INTERFACE_DATA, *PSP_DEVICE_INTERFACE_DATA;
    """
    _fields_ = [
        ('cbSize', DWORD),
        ('InterfaceClassGuid', GUID),
        ('Flags', DWORD),
        ('Reserved', ULONG_PTR),
    ]

    def __str__(self):
        return "InterfaceClassGuid:%s Flags:%s" % (
            self.InterfaceClassGuid, self.Flags)


PSP_DEVICE_INTERFACE_DATA = ctypes.POINTER(SP_DEVICE_INTERFACE_DATA)
PSP_DEVICE_INTERFACE_DETAIL_DATA = ctypes.c_void_p


class dummy(ctypes.Structure):
    """
    A dummy structure to provide a size of a structure 
    with two fields d1 (DWORD) and d2 (CHAR)
    """
    _fields_ = [("d1", DWORD), ("d2", WCHAR)]
    _pack_ = 1


SIZEOF_SP_DEVICE_INTERFACE_DETAIL_DATA_W = ctypes.sizeof(dummy)


SetupDiDestroyDeviceInfoList = ctypes.windll.setupapi.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.argtypes = [HDEVINFO]
SetupDiDestroyDeviceInfoList.restype = BOOL

SetupDiGetClassDevs = ctypes.windll.setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [ctypes.POINTER(GUID), PCTSTR, HWND, DWORD]
SetupDiGetClassDevs.restype = ValidHandle  # HDEVINFO

SetupDiEnumDeviceInterfaces = ctypes.windll.setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.argtypes = [
    HDEVINFO,
    PSP_DEVINFO_DATA,
    ctypes.POINTER(GUID),
    DWORD,
    PSP_DEVICE_INTERFACE_DATA]
SetupDiEnumDeviceInterfaces.restype = BOOL

CM_Get_Parent = ctypes.windll.setupapi.CM_Get_Parent
CM_Get_Device_ID = ctypes.windll.setupapi.CM_Get_Device_IDW


SetupDiGetDeviceInterfaceDetail = ctypes.windll.setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HDEVINFO,
    PSP_DEVICE_INTERFACE_DATA,
    PSP_DEVICE_INTERFACE_DETAIL_DATA,
    DWORD,
    PDWORD,
    PSP_DEVINFO_DATA]
SetupDiGetDeviceInterfaceDetail.restype = BOOL


"""
BOOL SetupDiGetDeviceRegistryProperty(
  _In_      HDEVINFO         DeviceInfoSet,
  _In_      PSP_DEVINFO_DATA DeviceInfoData,
  _In_      DWORD            Property,
  _Out_opt_ PDWORD           PropertyRegDataType,
  _Out_opt_ PBYTE            PropertyBuffer,
  _In_      DWORD            PropertyBufferSize,
  _Out_opt_ PDWORD           RequiredSize
);
"""
SetupDiGetDeviceRegistryProperty = ctypes.windll.setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.argtypes = [
    HDEVINFO, PSP_DEVINFO_DATA, DWORD, PDWORD, PBYTE, DWORD, PDWORD]
SetupDiGetDeviceRegistryProperty.restype = BOOL


"""
BOOL SetupDiOpenDeviceInfo(
  _In_      HDEVINFO         DeviceInfoSet,
  _In_      PCTSTR           DeviceInstanceId,
  _In_opt_  HWND             hwndParent,
  _In_      DWORD            OpenFlags,
  _Out_opt_ PSP_DEVINFO_DATA DeviceInfoData
);
"""


GUID_CLASS_COMPORT = GUID(0x86e0d1e0,
                          0x8089,
                          0x11d0,
                          (ctypes.c_ubyte * 8)(0x9c,
                                               0xe4,
                                               0x08,
                                               0x00,
                                               0x3e,
                                               0x30,
                                               0x1f,
                                               0x73))

GUID_DEVINTERFACE_USB_PRINT = GUID(0x28d78fad,
                                   0x5a12,
                                   0x11d1,
                                   (ctypes.c_ubyte * 8)(0xae,
                                                        0x5b,
                                                        0x00,
                                                        0x00,
                                                        0xf8,
                                                        0x03,
                                                        0xa8,
                                                        0xc2))

"""
The GUID_DEVINTERFACE_USB_DEVICE device interface class is defined for USB devices
that are attached to a USB hub.
Identifier GUID_DEVINTERFACE_USB_DEVICE
Class GUID {A5DCBF10-6530-11D2-901F-00C04FB951ED}

The system-supplied USB hub driver registers instances of GUID_DEVINTERFACE_USB_DEVICE to 
notify the system and applications of the presence of USB devices that are attached to a USB hub.
"""
GUID_DEVINTERFACE_USB_DEVICE = GUID(0xA5DCBF10,
                                    0x6530,
                                    0x11D2,
                                    (ctypes.c_ubyte * 8)(0x90,
                                                         0x1F,
                                                         0x00,
                                                         0xC0,
                                                         0x4f,
                                                         0xb9,
                                                         0x51,
                                                         0xed))



"""
The GUID_DEVINTERFACE_IMAGE device interface class is defined for WIA devices and Still Image (STI) devices, 
including digital cameras and scanners.
Identifier GUID_DEVINTERFACE_IMAGE
Class GUID {6BDD1FC6-810F-11D0-BEC7-08002BE2092F}
"""
GUID_DEVINTERFACE_SCAN_DEVICE = GUID(0x6BDD1FC6,
                                     0x810F,
                                     0x11D0,
                                     (ctypes.c_ubyte * 8)(0xBE,
                                                          0xC7,
                                                          0x08,
                                                          0x00,
                                                          0x2B,
                                                          0xE2,
                                                          0x09,
                                                          0x2F))

GUID_DEVINTERFACE_WINUSB_DEVICE = GUID(0x573e8c73,
                                       0x0cb4,
                                       0x4471,
                                       (ctypes.c_ubyte * 8)(0xa1,
                                                            0xbf,
                                                            0xfa,
                                                            0xb2,
                                                            0x6c,
                                                            0x31,
                                                            0xd3,
                                                            0x85))
