"""
LEDM wrapper around Copy related treee

"""
import logging
log = logging.getLogger(__name__)


from collections import namedtuple
from . import ledm_templates
from .ledm_tree import LEDMTree



class CopyConfigDyn(LEDMTree):
    """
    CopyConfigDyn tree /DevMgmt/CopyConfigDyn.xml
    """
    def __init__(self, data=ledm_templates.COPY_CONFIG_DYN):
        super().__init__(data)
	
    def default_media_size_name(self):
        """
        read/write the default media size name
        """
        return self.get("DefaultMediaSizeName")

		
    def default_media_size_name(self, value):
        self.set("DefaultMediaSizeName", value)
