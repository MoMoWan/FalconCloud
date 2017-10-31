"""
LEDM wrapper around Product related treee

"""
import logging
from collections import defaultdict
from . import ledm_templates
from .ledm_tree import LEDMTree
log = logging.getLogger(__name__)


class EICommand(LEDMTree):
    """
    EICommand tree /DevMgmt/EICommand.xml
    """
    def __init__(self, data=ledm_templates.EICOMMAND_TEMPLATE):
        super().__init__(data)

    @property
    def command(self, cmd):
        self.get("decCommand")

    @command.setter
    def command(self, value):
        self.set("decCommand", value)


class EIStatusVars(LEDMTree):
    """
    EIStatusVars tree /DevMgmt/EIStatusVars.xml
    """
    def __init__(self, data):
        super().__init__(data)

    @property
    def status_registers(self):
        """
        return a dictionary of Status registers
        """
        engine_status_vars = defaultdict(lambda: "0001")
        nodes = self.data.findAll("Variable")
        for node in nodes:
            try:
                name = "SR{}".format(int(node.find("Name").text))
                value = node.find("Value").text
                engine_status_vars[name] = value
            except:
                pass

        return engine_status_vars

