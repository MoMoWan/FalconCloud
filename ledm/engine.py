"""
This is specific functions for Engine commands
"""
import logging
log = logging.getLogger(__name__)

from collections import defaultdict
import time
from . import ledm_api
from .trees import ledm_templates
from .trees.ledm_tree import LEDMTree


def get_engine_status_registers():
    """
    Gets a dictionary of status regsiters, if the status
    register does not exist it will return "0001"

    Args:

    Returns:
        defaultdict: dictionary of status registers
    """
    engine_status_vars = defaultdict(lambda: "0001")
    tree = ledm_api.get("/DevMgmt/EIStatusVars.xml")
    nodes = tree.data.findAll("Variable")
    for node in nodes:
        try:
            name = "SR{}".format(int(node.find("Name").text))
            value = node.find("Value").text
            engine_status_vars[name] = value
        except:
            pass

    return engine_status_vars


def get_engine_status_register(status_register):
    """
    This gets the value of the status register. It will 
    send down the engine status register command. 

    Args:
        status_register (str): status register command in the 
            form of SRxxx 

    Returns:`
        str: hex string of the status register command
    """
    if not status_register.upper().startswith("SR"):
        raise ValueError("Status Register must start with SR")
    send_command(status_register)
    return get_engine_status_registers()[status_register]


def wait_for_status_register_value(status_register, bitwise_op, expected_value, mask_value, time_to_wait, sleep_time=0.1,):
    """
    Wait for status register value with bitmask value to match with the expected_value
    Args:
        status_register (str): status register number
        bitwise_op (str): "AND", "OR", "XOR" bitwise operation
        expected_value (int): the expected value after bitwise op
        mask_value (int): The mask value 
        time_to_wait (int): how long to wait for expected_value
        sleep_time (float): loop delay
    """
    mask_dict = {
        "AND": lambda x, y: x & y,
        "OR": lambda x, y: x | y,
        "XOR": lambda x, y: x ^ y,
    }

    if isinstance(expected_value, str):
        # Assumption hex string
        expected_value = int(expected_value, 16)

    if isinstance(mask_value, str):
        # Assumption hex string
        mask_value = int(mask_value, 16)

    if isinstance(time_to_wait, str):
        # Assumption hex string
        mask_value = int(time_to_wait)

    start_time = time.time()
    elapsed_time = time.time() - start_time
    while elapsed_time < time_to_wait:
        try:
            sr_value = int(get_engine_status_register(status_register), 16)
            if mask_dict[bitwise_op.upper()](sr_value, mask_value) == expected_value:
                return True, sr_value
        except:
            time.sleep(sleep_time)
            elapsed_time = time.time() - start_time
    return False, sr_value


def send_printer_info_index(eec111, eec112, eec113):
    """The send_printer_info_index command allows one to capture engine data 
    to a log to verify proper engine function. Use empty brackets "()" to clear indexes.

    It will send these commands in this order
    eec111
    eec113
    eec112

    Args:
        eec111: The EEC111 engine command
        eec112: The EEC112 engine command
        eec113: The EEC113 engine command

    Example:
        engine.send_printer_info_index(eec111="0xEB46",eec112="0xEE01",eec113="0xEC24")

    """
    send_command(eec111)
    send_command(eec113)
    send_command(eec112)


def send_command(engine_command):
    """
    This will send an engine command. It can be an engine command or status register

    Args:
        str: engine command or status register

    Example:
        engine.send_command("0xEB46")
        engine.send_command("SR1")

    """
    if engine_command.upper().startswith("SR"):
        engine_command = _convert_to_sr_to_engine_command(engine_command)
    temp_engine_command = engine_command
    engine_command = int(engine_command, 16)
    log.debug("engine_command = int {} hex {}".format(engine_command, temp_engine_command))
    tree_engine_cmd = LEDMTree(ledm_templates.EICOMMAND_TEMPLATE)
    tree_engine_cmd.set("decCommand", str(engine_command))
    ledm_api.put("/DevMgmt/EICommand.xml", tree_engine_cmd)


def _convert_to_sr_to_engine_command(status_register):
    """
    utility method to convert status register to engine command

    Args:
        status_register (str): Status Regsiter like SRxxx

    Returns:
        str: hex string of the engine command
    """
    if not status_register.upper().startswith("SR"):
        return status_register
    if status_register.upper().startswith("SR"):
        status_register = status_register[2:]

    int_value = int(str(status_register))
    status_reg_bin = bin(int_value) + "0"
    status_reg_bin = status_reg_bin[2:]
    status_reg_bin = status_reg_bin.zfill(16)
    if status_reg_bin.count('1') % 2 == 0:
        status_reg_bin = status_reg_bin[:-1] + '1'

    return hex(int(status_reg_bin, 2))[2:].zfill(4)


def convert_hex_to_bin(cmd):
    """
    Engine strin gHex Command convert to string
    binary format

    Args:
        cmd (str): hex command
    
    Returns:
        str: string binary format
    """
    status_reg = bin(int(str(cmd), 16))
    status_reg = status_reg.replace("0b", "")
    return status_reg.zfill(16)
