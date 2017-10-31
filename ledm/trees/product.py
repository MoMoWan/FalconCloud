"""
LEDM wrapper around Product related treee

"""
import logging
from . import ledm_templates
from .ledm_tree import LEDMTree
log = logging.getLogger(__name__)


class ProductConfigDyn(LEDMTree):
    """
    ProductConfigDyn tree /DevMgmt/ProductConfigDyn.xml
    """
    def __init__(self, data=ledm_templates.PRODUCT_CONFIG_DYN):
        super().__init__(data)

    @property
    def auto_off_time(self):
        """
        Read/Write AutoOffTime
        """
        return self.get("AutoOffTime")

    @auto_off_time.setter
    def auto_off_time(self, value):
        if not value.endswith("minutes"):
            raise ValueError("auto_off_time illegal value {}".format(value))
        self.set("AutoOffTime", value)

    @property
    def device_languague(self):
        """
        Read/Write DeviceLanguage
        """
        return self.get("DeviceLanguage")

    @device_languague.setter
    def device_languague(self, value):
        if not value.endswith("minutes"):
            raise ValueError("device_languague illegal value {}".format(value))
        self.set("DeviceLanguage", value)

    @property
    def device_location(self):
        """
        Read/Write DeviceLocation
        """
        return self.get("DeviceLocation")

    @device_location.setter
    def device_location(self, value):
        if not value.endswith("minutes"):
            raise ValueError("device_location illegal value {}".format(value))
        self.set("DeviceLocation", value)

    @property
    def duplex_binding_option(self):
        """
        Read/Write DuplexBindingOption
        """
        return self.get("DuplexBindingOption")

    @property
    def duplex_unit(self):
        """
        Read DuplexUnit element
        """
        return self.get("DuplexUnit")

    @property
    def engine_fw_rev(self):
        """
        returns the engine fw revision
        """
        return self.get("ModelNumber[0]")

    @property
    def fax(self):
        """
        returns Fax element
        """
        return self.get("Fax")

    @property
    def formatter_fw_rev(self):
        """
        returns the engine fw revision
        """
        return self.get("Date")

    @property
    def formatter_serial_number(self):
        """
        returns the formatter serial number
        """
        return self.get("ModelNumber[1]")

    @property
    def languages(self):
        """
        Return a list of languages supported
        Args:

        Returns:
            [str]: a list of languages

        """
        nodes = self.data.findAll("Language")
        languages = []
        for node in nodes:
            languages.append(node.text)

        return languages

    @property
    def power_save_timeout(self):
        """
        Read/Write PowerSaveTimeout
        """
        return self.get("PowerSaveTimeout")

    @power_save_timeout.setter
    def power_save_timeout(self, value):
        if not value.endswith("minutes"):
            raise ValueError("power_save_timeout illegal value {}".format(value))
        self.set("PowerSaveTimeout", value)


class ProductLogsConfigDyn(LEDMTree):
    """
    ProductConfigDyn tree /DevMgmt/ProductLogsConfigDyn.xml
    """
    def __init__(self, data):
        super().__init__(data)

    @property
    def event_logs(self):
        """
        return a list of event codes
        """

        event_codes = []
        event_code_nodes = self.data.findAll("EventCode")
        for event_code_node in event_code_nodes:
            event_codes.append(event_code_node.text)
        return event_codes

