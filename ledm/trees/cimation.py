"""
LEDM rapper around CIMation LEDM tree
"""

import logging
from . import ledm_templates
from .ledm_tree import LEDMTree

log = logging.getLogger(__name__)


class CIMation(LEDMTree):
    """
    CIMation tree that provides methods
    """

    def __init__(self, data=ledm_templates.CIMATION):
        super().__init__(data)

    @property
    def scan_1200_color_calibration(self):
        """
        1200 Scanner Color Calibration data
        """
        return self.get("SCAN-CALIBRATION-DOWNLOAD-1200")

    @scan_1200_color_calibration.setter
    def set_1200_color_calibration(self, value):
        self.set("SCAN-CALIBRATION-DOWNLOAD-1200", value)

    @property
    def scan_600_color_calibration(self):
        """
        1200 Scanner Color Calibration data
        """
        return self.get("SCAN-CALIBRATION-DOWNLOAD-600")

    @scan_600_color_calibration.setter
    def set_600_color_calibration(self, value):
        self.set("SCAN-CALIBRATION-DOWNLOAD-600", value)

    @property
    def scan_300_color_calibration(self):
        """
        1200 Scanner Color Calibration data
        """
        return self.get("SCAN-CALIBRATION-DOWNLOAD-300-COLOR")

    @scan_300_color_calibration.setter
    def set_300_color_calibration(self, value):
        self.set("SCAN-CALIBRATION-DOWNLOAD-300-COLOR", value)

    @property
    def scan_300_mono_calibration(self):
        """
        1200 Scanner Color Calibration data
        """
        return self.get("SCAN-CALIBRATION-DOWNLOAD-300-MONO")

    @scan_300_mono_calibration.setter
    def set_300_mono_calibration(self, value):
        self.set("SCAN-CALIBRATION-DOWNLOAD-300-MONO", value)

    @property
    def scanner_lamp_gain_value(self):
        """
        Scanner Lamp Gain Value
        """
        return self.get("SCANNER-LAMP-GAIN-VALUE")

    @property
    def scanner_reference_position(self):
        """
        Scanner Lamp Gain Value
        """
        return self.get("SCANNER-REFERENCE-POSITION")

    @property
    def scanner_scanline_statistics(self):
        """
        Scanner Lamp Gain Value
        """
        return self.get("SCANNER-SCANLINE-STATISTICS")

    @property
    def scanner_eduplex_config(self):
        """
        Scanner Lamp Gain Value
        """
        return self.get("SCANNER-SCANNER-EDUPLEX-CONFIG")

    @property
    def scan_image_processing(self):
        """
        Scan Image processing 
        Currently we supports 
            none - removes none
            all - removes all
            10to8 - removes 10to8
            3x3 - removes 3x3 

        For example, if you need to set it to remove all, 
        you should send a put request to CIMation.xml,
        """
        return self.get("SCAN-IMAGE-PROCESSING")

    @scan_image_processing.setter
    def scan_image_processing(self, value):
        """
        Sets SCAN-IMAGE-PROCESSING only possible values
        are none, all, 10to8, 3x3
        """
        possible_values = ("none", "all", "10to8", "3x3")
        if value not in possible_values:
            raise ValueError("Unknown value {} olnly supports {}".format(value, possible_values))

        self.set("SCAN-IMAGE-PROCESSING", value)