"""
Manufacturing related Tree
"""

import logging
log = logging.getLogger(__name__)


from collections import namedtuple
from . import ledm_templates
from .ledm_tree import LEDMTree


class ManufacturingConfigDyn(LEDMTree):
    """
    ManufacturingConfigDyn Tree
    """
    def __init__(self, data=ledm_templates.MANUFACTURING_CONFIG_DYN):
        super().__init__(data)

    @property
    def clear_all_counter(self):
        """
        Write only ClearAllCounters
        """
        raise ValueError("clear_all_counters is write only")

    @clear_all_counter.setter
    def clear_all_counter(self, value):
        if value not in ["true", "false"]:
            raise ValueError(
                "clear_all_counters valid values are true or false given {}".format(value))
        self.set("ClearAllCounters", value)

    @property
    def cold_reset_language_no_reboot(self):
        """
        read/write the ColdResetLanguageNoReboot
        """
        return self.get("ColdResetLanguageNoReboot")

    @cold_reset_language_no_reboot.setter
    def cold_reset_language_no_reboot(self, value):
        self.set("ColdResetLanguageNoReboot", value)

    @property
    def control_panel_display_string(self):
        """
        get the current control panel display string

        Returns:
            str
        """
        return self.get("ControlPanelDisplayString")

    @property
    def control_panel_info(self):
        """
        Return Control Panel Information such as CP Project ID, CP Code Version,
        CP ID, CP LCD Vendor.

        Returns:
            ControlPanelInfo: namedtuple ControlPanel
        """
        ControlPanelInfo = namedtuple("ControlPanelInfo", "project_id code_version id_value lcd_vendor")
        control_panel_info = self.data.find("ControlPanelInfo")
        if control_panel_info:
            project_id = control_panel_info.find("ControlPanelProjectID") if control_panel_info.find("ControlPanelProjectID") else ""
            version = control_panel_info.find("ControlPanelCodeVersion") if control_panel_info.find("ControlPanelCodeVersion") else ""
            id_value = control_panel_info.find("ControlPanelID") if control_panel_info.find("ControlPanelID") else ""
            lcd_vendor = control_panel_info.find("ControlPanelLcdVendor") if control_panel_info.find("ControlPanelLcdVendor") else ""
            return ControlPanelInfo(project_id, version, id_value, lcd_vendor)
        else:
            raise ValueError("ControlPanelInfo not present in ManufacturingConfigDyn Tree")

    @property
    def control_panel_button_press(self):
        """
        Write ControlPanelButtonPress element
        """
        return self.get("ControlPanelButtonPress")

    @control_panel_button_press.setter
    def control_panel_button_press(self, value):
        """
        Write ControlPanelButtonPress element
        """
        self.set("ControlPanelButtonPress", value)

    @property
    def control_panel_virtual_button_press(self):
        """
        Write ControlPanelVirtualButtonPress element
        """
        return self.get("ControlPanelVirtualButtonPress")

    @control_panel_virtual_button_press.setter
    def control_panel_virtual_button_press(self, value):
        self.set("ControlPanelVirtualButtonPress", value)

    @property
    def country_and_region_name_noreboot(self):
        """
        Read/Write CountryAndRegionNameNoReboot element
        """
        return self.get("CountryAndRegionNameNoReboot")

    @country_and_region_name_noreboot.setter
    def country_and_region_name_noreboot(self, value):
        self.set("CountryAndRegionNameNoReboot", value)

    @property
    def custom_product_number(self):
        """
        read/write the custom product number
        """
        return self.get("CustomProductNumber")

    @custom_product_number.setter
    def custom_product_number(self, value):
        self.set("CustomProductNumber", value)

    @property
    def dcc_nvram_restore(self):
        """
        read/write the product number
        """
        return self.get("DCCNvramRestore")

    @dcc_nvram_restore.setter
    def dcc_nvram_restore(self, value):
        expected_value = ["enabled", "disabled"]
        if value not in expected_value:
            raise ValueError("DCCNvramRestore\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("DCCNvramRestore", value)

    @property
    def formatter_serial_number(self):
        """
        Read/Write Formatter Serial Number
        """
        return self.get("ModelNumber")

    @formatter_serial_number.setter
    def formatter_serial_number(self, value):
        self.set("BoardTypeEnum", "systemControl")
        self.set("ModelNumber", value)

    @property
    def generic_prompt(self):
        """
        read/write the generic prompt
        """
        return self.get("GenericPrompt")

    @generic_prompt.setter
    def generic_prompt(self, value):
        if value not in ["enabled", "disabled"]:
            raise ValueError(
                "generic prompt can only be enabled/disabled given {}".format(value))
        self.set("GenericPrompt", value)

    @property
    def install_date(self):
        """
        read/write the InstallDate
        """
        return self.get("InstallDate")

    @install_date.setter
    def install_date(self, value):
        self.set("InstallDate", value)

    @property
    def isa_power(self):
        """
        read/write ISA Power
        """
        return self.get("ISAPower")

    @isa_power.setter
    def isa_power(self, value):
        if value not in ["enabled", "disabled", "0", "1"]:
            raise ValueError("ISAPower invalid value {}".format(value))
        self.set("ISAPower", value)

    @property
    def mac_address(self):
        """
        Read/Write MAC Address
        """
        return self.get("HardwareAddress")

    @mac_address.setter
    def mac_address(self, value):
        self.set("HardwareAddress", value)

    @property
    def make_and_model(self):
        """
        read/write the product number
        """
        return self.get("MakeAndModel")

    @make_and_model.setter
    def make_and_model(self, value):
        self.set("MakeAndModel", value)

    @property
    def manufacturing_mode_preset(self):
        """
        read/write the product number
        """
        return self.get("ManufacturingModePreset")

    @manufacturing_mode_preset.setter
    def manufacturing_mode_preset(self, value):
        expected_value = ["off", "on"]
        if value not in expected_value:
            raise ValueError("ManufacturingModePreset\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("ManufacturingModePreset", value)

    @property
    def mfg_status(self):
        """
        MFG Status nodes
        """
        mfg_status_nodes = []
        MfgStatus = namedtuple("MfgStatus", "id_value value")
        mfg_status_raw_nodes = self.get("MfgStatus", True)
        for mfg_status_raw_node in mfg_status_raw_nodes:
            id_value = ""
            value = ""
            for child in mfg_status_raw_node.children:
                if child.name is None:
                    continue
                elif "ID" in child.name:
                    id_value = child.text
                else:
                    value = child.text
            mfg_status_nodes.append(MfgStatus(id_value, value))
        return mfg_status_nodes

    @property
    def mfg_status_4(self):
        """
        MFG Status Node 
        ID4 = CurrentRegion,
        """
        target_node = "4"
        mfg_status_nodes = self.mfg_status
        for node in mfg_status_nodes:
            if node.id_value == target_node:
                return node.value
        raise ValueError("MfgStatus ID {} does not exist".format(target_node))

    @property
    def mfg_status_5(self):
        """
        MFG Status node
        ID5 = PreviousRegion
        """
        target_node = "5"
        mfg_status_nodes = self.mfg_status
        for node in mfg_status_nodes:
            if node.id_value == target_node:
                return node.value
        raise ValueError("MfgStatus ID {} does not exist".format(target_node))

    @property
    def mfg_status_6(self):
        """
        MFG Status node
        ID6 = RegionCount
        """
        target_node = "6"
        mfg_status_nodes = self.mfg_status
        for node in mfg_status_nodes:
            if node.id_value == target_node:
                return node.value
        raise ValueError("MfgStatus ID {} does not exist".format(target_node))

    @property
    def memory_crc(self):
        """
        read MemoryCRC element
        """
        return self.get("MemoryCRC")

    @property
    def nfc_card_detected(self):
        """
        read NFC Card Supported
        """
        value = self.get("NFCCardDetected")
        if value == "":
            return "false"
        return "true"

    @property
    def network_support(self):
        """
        read/write the product number
        """
        return self.get("NetworkSupport")

    @network_support.setter
    def network_support(self, value):
        expected_value = ["enabled", "disabled"]
        if value not in expected_value:
            raise ValueError("NetworkSupport\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("NetworkSupport", value)

    @property
    def page_counts_mono(self):
        """
        read/write mono pages
        """
        return self.get("MonochromeImpressions")

    @page_counts_mono.setter
    def page_counts_mono(self, value):
        # try to convert to integer to determine valid
        # number if not it should raise exception
        int(value)
        self.set("MonochromeImpressions", value)

    @property
    def page_counts_color(self):
        """
        read/write mono pages
        """
        return self.get("MonochromeImpressions")

    @page_counts_color.setter
    def page_counts_color(self, value):
        # try to convert to integer to determine valid
        # number if not it should raise exception
        int(value)
        self.set("MonochromeImpressions", value)

    @property
    def power_save_timeout_default(self):
        """
        read/write the product number
        """
        return self.get("PowerSaveTimeoutDefault")

    @power_save_timeout_default.setter
    def power_save_timeout_default(self, value):
        self.set("PowerSaveTimeoutDefault", value)

    @property
    def print_mode_override(self):
        """
        read/write the product number
        """
        return self.get("PrintModeOverride")

    @print_mode_override.setter
    def print_mode_override(self, value):
        expected_value = ["enabled", "disabled"]
        if value not in expected_value:
            raise ValueError("PrintModeOverride\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("PrintModeOverride", value)

    @property
    def print_engine_test_abort_cal(self):
        """
        read/write the serial number
        """
        return self.get("PrintEngineTestAbortCalibration")

    @print_engine_test_abort_cal.setter
    def print_engine_test_abort_cal(self, value):
        expected_value = ["true", "false"]
        if value not in expected_value:
            raise ValueError("print_engine_test_abort_cal\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("PrintEngineTestAbortCalibration", value)

    @property
    def printer_general_reset(self):
        """
        Write PrinterGeneralReset element
        """
        raise ValueError("printer_general_reset is write only")

    @printer_general_reset.setter
    def printer_general_reset(self, value):
        self.set("PrinterGeneralReset", value)

    @property
    def product_number(self):
        """
        read/write the product number
        """
        return self.get("ProductNumber")

    @product_number.setter
    def product_number(self, value):
        self.set("ProductNumber", value)


    @property
    def reboot_on_error(self):
        """
        read/write the serial number
        """
        return self.get("RebootOnError")

    @reboot_on_error.setter
    def reboot_on_error(self, value):
        expected_value = ["enabled", "disabled"]
        if value not in expected_value:
            raise ValueError("RebootOnError\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("RebootOnError", value)

    @property
    def revision(self):
        """
        get the current revision
        """
        return self.get("Revision")

    @property
    def serial_number(self):
        """
        read/write the serial number
        """
        return self.get("SerialNumber")

    @serial_number.setter
    def serial_number(self, value):
        if len(value) != 10:
            raise ValueError("SerialNumber must be 10 characters long given {}".format(value))
        self.set("SerialNumber", value)

    @property
    def service_error_log_clear(self):
        """
        Write service_error_log_clear element
        """
        raise ValueError("service_error_log_clear is write only")

    @service_error_log_clear.setter
    def service_error_log_clear(self, value):
        expected_value = ["true", "false"]
        if value not in expected_value:
            raise ValueError("ServiceErrorLogClear\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("ServiceErrorLogClear", value)

    @property
    def service_id(self):
        """
        read/write the service id
        """
        return self.get("ServiceID")

    @service_id.setter
    def service_id(self, value):
        self.set("ServiceID", value)

    @property
    def setup_prompt(self):
        """
        read/write SetupPrompt
        """
        return self.get("SetupPrompt")

    @setup_prompt.setter
    def setup_prompt(self, value):
        expected_value = ["enabled", "disabled"]
        if value not in expected_value:
            raise ValueError("SetupPrompt\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("SetupPrompt", value)

    @property
    def ssa_bottom_led_correction(self):
        """
        read/write the serial number
        """
        return self.get("SSABottomLedCorrection")

    @ssa_bottom_led_correction.setter
    def ssa_bottom_led_correction(self, value):
        self.set("SSABottomLedCorrection", value)

    @property
    def ssa_top_led_correction(self):
        """
        read/write the serial number
        """
        return self.get("SSATopLedCorrection")

    @ssa_top_led_correction.setter
    def ssa_top_led_correction(self, value):
        self.set("SSATopLedCorrection", value)

    @property
    def system_show_energy_logo(self):
        """
        read/write the serial number
        """
        return self.get("SystemShowEnergyLogo")

    @system_show_energy_logo.setter
    def system_show_energy_logo(self, value):
        expected_value = ["true", "false"]
        if value not in expected_value:
            raise ValueError("SystemShowEnergyLogo\nreceived{}\nexpected:{}".format(
                value,
                expected_value))
        self.set("SystemShowEnergyLogo", value)

    @property
    def wireless_card_detected(self):
        """
        read Wireless Card Supported
        """
        value = self.get("WirelessCardDetected")
        if value == "":
            return "false"
        return "true"

    def set_mfg_status(self, id_num, value, index=0):
        """
        Set MfgSupport Node
        """
        mfg_status_raw_nodes = self.data.findAll("MfgSupport")
        if index > len(mfg_status_raw_nodes):
            raise IndexError("MfgStatus Node index {} out of bounds".format(index))

        target_node = mfg_status_raw_nodes[index]
        target_node.find("ID").string = str(id_num)
        target_node.find("ValueInt").string = str(value)