"""
LEDM wrapper around Product related treee

"""
import logging
from . import ledm_templates
from .ledm_tree import LEDMTree
log = logging.getLogger(__name__)


class MediaDyn(LEDMTree):
    """
    MediaDyn tree /DevMgmt/MediaDyn.xml
    """
    def __init__(self, data=ledm_templates.MEDIA_DYN):
        super().__init__(data)

    @property
    def media_size_name(self):
        """
        Read/Write MediaSizeName
        """
        return self.get("MediaSizeName")

    @media_size_name.setter
    def media_size_name(self, value):
        self.set("MediaSizeName", value)

    @property
    def media_type(self):
        """
        Read/Write MediaType
        """
        return self.get("MediaType")

    @media_type.setter
    def media_type(self, value):
        self.set("MediaType", value)


class MediaHandlingDyn(LEDMTree):
    """
    MediaHandlingDyn /DevMgmt/MediaHandlingDyn.xml tree
    """
    def __init__(self, data=ledm_templates.MEDIA_HANDLING_DYN):
        super().__init__(data)

    @property
    def input_tray1_bin(self):
        """
        Read/Write //mhdyn:InputTray[1]/dd:InputBin
        """
        self.get("InputBin[1]")

    @input_tray1_bin.setter
    def input_tray1_bin(self, value):
        self.set("InputBin[1]", value)

    @property
    def input_tray1_media_type(self):
        """
        Read/Write //mhdyn:InputTray[1]/dd:MediaType
        """
        self.get("MediaType[1]")

    @input_tray1_media_type.setter
    def input_tray1_media_type(self, value):
        self.set("MediaType[1]", value)

    @property
    def input_tray1_media_size_name(self):
        """
        Read/Write //mhdyn:InputTray[1]/dd:MediaSizeName
        """
        self.get("MediaSizeName[1]")

    @input_tray1_media_size_name.setter
    def input_tray1_media_size_name(self, value):
        self.set("MediaSizeName[1]", value)
    
    @property
    def input_tray2_bin(self):
        """
        Read/Write //mhdyn:InputTray[2]/dd:InputBin
        """
        self.get("InputBin[2]")

    @input_tray2_bin.setter
    def input_tray2_bin(self, value):
        self.set("InputBin[2]", value)

    @property
    def input_tray2_media_type(self):
        """
        Read/Write //mhdyn:InputTray[2]/dd:MediaType
        """
        self.get("MediaType[2]")

    @input_tray2_media_type.setter
    def input_tray1_media_type(self, value):
        self.set("MediaType[2]", value)

    @property
    def input_tray2_media_size_name(self):
        """
        Read/Write //mhdyn:InputTray[2]/dd:MediaSizeName
        """
        self.get("MediaSizeName[2]")

    @input_tray2_media_size_name.setter
    def input_tray2_media_size_name(self, value):
        self.set("MediaSizeName[2]", value)

    @property
    def input_tray3_bin(self):
        """
        Read/Write //mhdyn:InputTray[3]/dd:InputBin
        """
        self.get("InputBin[3]")

    @input_tray3_bin.setter
    def input_tray2_bin(self, value):
        self.set("InputBin[3]", value)

    @property
    def input_tray3_media_type(self):
        """
        Read/Write //mhdyn:InputTray[3]/dd:MediaType
        """
        self.get("MediaType[3]")

    @input_tray3_media_type.setter
    def input_tray1_media_type(self, value):
        self.set("MediaType[3]", value)

    @property
    def input_tray3_media_size_name(self):
        """
        Read/Write //mhdyn:InputTray[3]/dd:MediaSizeName
        """
        self.get("MediaSizeName[3]")

    @input_tray3_media_size_name.setter
    def input_tray3_media_size_name(self, value):
        self.set("MediaSizeName[3]", value)
    



