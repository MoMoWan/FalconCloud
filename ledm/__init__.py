"""

Example Usage:

# Set IO type Examples
ledm.set_io("USB")
ledm.set_io("USB", "USB001")
ledm.set_io("10.1.1.100")


# data model
mfg_data = ledm.get("ManufacturingConfigDyn")
print(mfg_data.formatter_serial_number)
mfg = ledm.MaufacturingConfigDyn(response.data)


# session base request
with ledm.request() as Session:
    response = session.get("ManufacturingConfigDyn")
    mfg = ledm.model.Manufacturing(response.data)
    product_


# engine commands
from ledm import engine
engine.send_engine_command("EC123")
engine.send_engine_command("SR123")
engine.send_engine_command("SR123")
engine.send_engine_command("SR123")
sr_values = engine.get_engine_status_registers()
print(sr_values["SR123"] )
engine.wait_for_status_register_value("SR123", "what", time_to_wait)

# scanner related
from ledm import scanner
scanner.initiate_calibration(300)
scanner.wait_for_calibration_complete()
scanner.get_led_info()
scanner.get_scanner_reference()
scanner.get_notch()
scanner.scanner_statics_line()
scanner.get_calibration_data()
scanner.get_servo_data()


# control panel
not sure yet

"""
from .ledm_api import (
    get,
    get_with_status_code,
    put,
    post,
    is_available,

)

import logging
from .ledm_io import set_io
from .ledm_io import set_http_scheme
from . import engine
from . import scan
from . import trees
from . import control_panel
from .ledm_api import MFG_PASSWORD
from . import internal_print_job
from .udw import send_udw

def create_settable_model(tree_name):
    """
    create a model with settable template

    Args:
        tree_name (str): The tree name to instantiate

    Returns:
        LedmTree: The base LedmTree base class
    """

    from .resource import TREE_MAPPING_TO_OBJECT
    return TREE_MAPPING_TO_OBJECT[tree_name]()

logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True