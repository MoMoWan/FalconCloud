"""
LEDM wrapper around Network related trees

"""

import logging
from . import ledm_templates
from .ledm_tree import LEDMTree
log = logging.getLogger(__name__)

class Adapters(LEDMTree):
    """
    Adapters tree /IoMgmt/Adapters
    """
    def __init__(self, data=ledm_templates.ADAPTERS):
        super().__init__(data)

    @property
    def power(self):
        """
        on/off settings for Power
        """
        return self.get("Power")    

    @power.setter
    def power(self, value):
        expected_values = ["on", "off"]
        if value not in expected_values:
            raise ValueError("power incorrect settings\Expected: {}\nReceived: {}".format(expected_values, value))

        self.set("Power", value)

    @property
    def power_level(self):
        """
        on/off settings for Power
        """
        return self.get("PowerLevel")

    


class NetAppsDyn(LEDMTree):
    """
    NetAppsDyn tree /DevMgmt/NetAppsDyn.xml
    """
    def __init__(self, data=ledm_templates.NET_APPS_DYN):
        super().__init__(data)

    @property
    def direct_print(self):
        """
        enable/disable DirectPrint
        """
        return self.get("DirectPrint")

    @direct_print.setter
    def direct_print(self, value):
        expected_values = ["enabled", "disabled"]
        if value not in expected_values:
            raise ValueError("direct_print incorrect settings\Expected: {}\nReceived: {}".format(expected_values, value))

        self.set("DirectPrint", value)

class NetAppsSecureDyn(LEDMTree):
    """
    NetAppsDyn tree /DevMgmt/NetAppsSecureDyn.xml
    """
    def __init__(self, data=ledm_templates.NET_APPS_SECURE_DYN):
        super().__init__(data)

    @property
    def state(self):
        """
        enable/disable DirectPrint
        """
        return self.get("State")

    @state.setter
    def state(self, value):
        expected_values = ["enabled", "disabled"]
        if value not in expected_values:
            raise ValueError("state incorrect settings\Expected: {}\nReceived: {}".format(expected_values, value))

        self.set("State", value)

class Wifi(LEDMTree):
    """
    Adapters Template for tree /IoMgmt/Adapters/Wifi0
    """
    def __init__(self, data=ledm_templates.ADAPTERS):
        super().__init__(data)

    @property
    def power(self):
        """
        on/off settings for Power
        """
        return self.get("Power")    

    @power.setter
    def power(self, value):
        expected_values = ["on", "off"]
        if value not in expected_values:
            raise ValueError("power incorrect settings\Expected: {}\nReceived: {}".format(expected_values, value))

        self.set("Power", value)

    @property
    def power_level(self):
        """
        on/off settings for Power
        """
        return self.get("PowerLevel")

class WifiNetworks(LEDMTree):
    """
    NetAppsDyn tree /DevMgmt/NetAppsSecureDyn.xml
    """
    def __init__(self, data):
        super().__init__(data)

    @property
    def ssid(self):
        """
        Return a list of SSIDs
        """
        ssids = []
        ssid_nodes = self.data.findAll("SSID")
        for ssid_nodes in ssid_nodes:
            ssids.append(ssid_nodes.text)
        return ssids


class WifiProfile(LEDMTree):
    """
    NetAppsDyn tree /DevMgmt/NetAppsSecureDyn.xml
    """
    def __init__(self, data=ledm_templates.WIFI_PROFILE):
        super().__init__(data)

    @property
    def locale(self):
        """
        Read/Write Locale
        """
        return self.get("Locale")

    @locale.setter
    def locale(self, value):
        self.set("Locale", value)




