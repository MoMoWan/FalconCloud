"""
LEDM Control Panel related function 

"""

import logging
log = logging.getLogger(__name__)
import requests

from . import ledm_api
from .trees.manufacturing import ManufacturingConfigDyn


def clear_button_history():
    """
    reset button history
    """
    mfg = ManufacturingConfigDyn()
    mfg.set_mfg_status("5632", "0", index=0)
    try:
        ledm_api.put("ManufacturingConfigDyn", mfg)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            # this means it is not supported
            log.debug("clear_button_history is not supported")
        else:
            raise

def is_button_supported(button_name):
    """
    Determines if this button is supported either as 
    a Hard, Virtual, or Scroll Button

    Args:
        button_name (str): The button name

    Returns:
        bool: True if supported or False not supported
    """
    
    mfg_cap = ledm_api.get("ManufacturingConfigCap")
    if _is_hard_button_supported(mfg_cap, button_name):
        return True
    elif _is_virtual_button_supported(mfg_cap, button_name):
        return True
    elif _is_scroll_button_supported(mfg_cap, button_name):
        return True
    
    return False

def lightup_led(id_num=5631, value=0x00):
    """
    Setting of the LEDs via the MfgSupport data structure in ManufacturingConfigDyn.xml tree

    LED_ALL_Blink : 
    <mcdyn:ID>5631</mcdyn:ID>
    <mcdyn:ValueInt>2</mcdyn:ValueInt>
    LED_ALL_Blink2: 
    <mcdyn:ID>5631</mcdyn:ID>
    <mcdyn:ValueInt>3</mcdyn:ValueInt>
    LED_ALL_Off:
    <mcdyn:ID>5631</mcdyn:ID>
    <mcdyn:ValueInt>1</mcdyn:ValueInt>
    LED_ALL_On:
    <mcdyn:ID>5631</mcdyn:ID>
    <mcdyn:ValueInt>0</mcdyn:ValueInt>
    LED_ATTENTION_Off:
    <mcdyn:ID>5378</mcdyn:ID>
    <mcdyn:ValueInt>1</mcdyn:ValueInt>
    LED_ATTENTION_On:
    <mcdyn:ID>5378</mcdyn:ID>
    <mcdyn:ValueInt>0</mcdyn:ValueInt>
    LED_READY_Off:
    <mcdyn:ID>5377</mcdyn:ID>
    <mcdyn:ValueInt>1</mcdyn:ValueInt>
    LED_READY_On:
    <mcdyn:ID>5377</mcdyn:ID>
    <mcdyn:ValueInt>0</mcdyn:ValueInt>
    LED_WIRELESS_Off: 
    <mcdyn:ID>5385</mcdyn:ID>
    <mcdyn:ValueInt>1</mcdyn:ValueInt>
    LED_WIRELESS_On: 
    <mcdyn:ID>5385</mcdyn:ID>
    <mcdyn:ValueInt>0</mcdyn:ValueInt>

    Args:

    id_num (int) - the id command to specify which led
    value (int) - the value of the command id to send down
                     
    """
    mfg = ManufacturingConfigDyn()
    mfg.set_mfg_status(id_num, value, index=0)
    ledm_api.put("ManufacturingConfigDyn", mfg)
   

def press_button(button_name):
    """
    Press the button. It determines the type of button hard, 
    virtual, or scroll and then presses it. 

    Args:
        button_name (str): the button name to press

    Raises:
        ValueError: If button is not supported 
    """
    
    mfg_cap = ledm_api.get("ManufacturingConfigCap")
    if _is_hard_button_supported(mfg_cap, button_name):
        press_hard_button(button_name)
    elif _is_virtual_button_supported(mfg_cap, button_name):
        press_virtual_button(button_name)
    elif _is_scroll_button_supported(mfg_cap, button_name):
        press_scroll_button(button_name)
    else:
        raise ValueError("{} button is not supported".format(button_name))


def press_hard_button(button_name):
    """
    Press Hard button 

    Args:
    button_name (str): button Name
    """
        
    mfg = ManufacturingConfigDyn()
    mfg.control_panel_button_press = button_name
    ledm_api.put("ManufacturingConfigDyn", mfg)

def press_virtual_button(button_name):
    """
    Press Virtual button 
    
    Args:
    button_name (str): button Name
    """
    mfg = ManufacturingConfigDyn()
    mfg.control_panel_virtual_button_press = button_name
    ledm_api.put("ManufacturingConfigDyn", mfg)

def press_scroll_button(button_name):
    """
    Press Scroll button 
    
    Args:
    button_name (str): button Name
    """
    mfg = ManufacturingConfigDyn()
    mfg.set("ControlPanelScroll", button_name) 
    ledm_api.put("ManufacturingConfigDyn", mfg)

def _is_hard_button_supported(mfg_cap, button_name):
    """
    Determines if button is a supported hard button  
    
    Args:
    mfg_cap (LEDMTree): LEDMTree object 
    button_name (str): button Name

    Returns:
        bool: True if supported else False 
    """
    nodes = mfg_cap.get("ControlPanelButtonPress", aslist=True)
    if nodes == "":
        return False
    for node in nodes:
        log.debug("node {}  type {}".format(node, type(node)))
        if button_name == node.text:
            return True
    return False

def _is_virtual_button_supported(mfg_cap, button_name):
    """
    Determines if button is a supported virtual button  
    
    Args:
    mfg_cap (LEDMTree): LEDMTree object
    button_name (str): button Name

    Returns:
        bool: True if supported else False 
    """
    nodes = mfg_cap.get("ControlPanelVirtualButtonPress", aslist=True)
    if nodes == "":
        return False
    for node in nodes:
        if button_name == node.text:
            return True
    return False

def _is_scroll_button_supported(mfg_cap, button_name):
    """
    Determines if button is a supported scroll button  
    
    Args:
    mfg_cap (LEDMTree): LEDMTree object
    button_name (str): button Name

    Returns:
        bool: True if supported else False 
    """
    nodes = mfg_cap.get("ControlPanelScroll", aslist=True)
    if nodes == "":
        return False
    for node in nodes:
        if button_name == node.text:
            return True
    return False
