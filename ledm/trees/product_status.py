"""
LEDM wrapper around ProductSatusDyn

"""
import logging
log = logging.getLogger(__name__)


from .ledm_tree import LEDMTree 

class ProductStatusDyn(LEDMTree):
    """
    Product Status LEDM Tree
    """
    def __init__(self, data):
        super().__init__(data)
    
    @property
    def status_category(self):
        """
        return the current printer status
        """
        return self.get("StatusCategory")

    @property
    def loc_string(self):
        """
        a list of Product Status Location string
        Returns:
            [str] : returns a list of status strings
        """
        nodes = self.data.findAll("LocString")
        loc = []
        for node in nodes:
            loc.append(node.text)
        return loc