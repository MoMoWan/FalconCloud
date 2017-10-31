"""
Omni User Interface module. It provides functionality to communicate with the control panel.

Helpful expression

.hp-constrained - ends with elements that are constrained
.disabled - ends with elements that are disabled
.hp-permission-denied - ends with elements that require permission

"""
__version__ = "$Revision: 47957 $"
__author__  = "$Author: dfernandez $"
__date__    = "$Date: 2016-05-27 14:37:21 -0600 (Fri, 27 May 2016) $ "
 
"""
To Do:

"""

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import time
import collections

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger("jedilib")

# =============================================================================
# .NET modules
# =============================================================================
import clr
from System import TimeSpan
import requests
requests.utils.should_bypass_proxies = lambda url: True


device_automation_dll = os.path.join(os.path.dirname(__file__), "DeviceAutomation-2.1.dll")
clr.AddReference(device_automation_dll)
from HP.DeviceAutomation.Jedi import JediOmniDevice, OmniElementState
from HP.DeviceAutomation.Jedi.OmniUserInteraction import OmniTesterClient, WebInspectorDisconnectedException, WebInspectorException
from HP.DeviceAutomation import Coordinate

jedi_dll = os.path.join(os.path.dirname(__file__), "HP.Falcon.JediNG.dll")
clr.AddReference(jedi_dll)
from HP.Falcon.JediNG.WebServices.Qualification.ControlPanel import ControlPanelQualificationServiceClient
from HP.Falcon.JediNG.WebServices.Qualification.ControlPanel import omni_enable, OxpdTestClient



# =============================================================================
# Globals and Definitions
# =============================================================================
class Property:
        Attribute  = 0
        Css = 1
        Property = 2

class ElementState:
    Constrained = 0
    Disabled = 1
    Enabled = 2
    Exists = 3
    Hidden = 4
    Locked = 5
    Selected = 6
    Useable = 7
    VisibleCompletely = 8
    VisiblePartially = 9

class OmniId:
    Self = 0
    Children = 1
    Descendants = 2
    Selected = 3

class PanelButton:
    Start = 0
    Stop = 1
    Sleep = 2
    Clear = 3
    Interrupt = 4
    Power = 5
    Help = 6
    Reset = 7
    Menu = 8
    Ok = 9
    Back = 10
    At = 11
    Folder = 12
    Home = 118
    Hash = 119
    Info = 120
    PrintFromJobStorage = 121
    MessageCenter = 122
    SignIn = 123
    

def omni_connection_handler(fn):
    def g(self, *args, **kwargs):
        if not OmniUI.connected:
            log.debug("Omni Conecting")
            try:
                self.connect()
            except WebInspectorException as ex:
                log.debug("WebInspector Disconnecting")
                self.disconnect()
                time.sleep(1)
                log.debug("Omni Connecting again")
                self.connect()
        try:            
            return fn(self, *args, **kwargs)
        except (WebInspectorDisconnectedException, WebInspectorException) as ex:
            self.disconnect()
            time.sleep(1)
            self.connect()
            return fn(self, *args, **kwargs)

    return g


class Singleton(type):
    _instance = None
    def __call__(cls, ip_address, adminpassowrd=""):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(
                ip_address, adminpassowrd)
        return cls._instance


class OmniUI(object, metaclass = Singleton):
    def __init__(self, ip_address, adminpassword = ""):
        self.ip_address = ip_address
        self.port = 9222
        self.omni_service = OmniTesterClient(ip_address, TimeSpan.FromSeconds(30))
        OmniUI.connected = False

    def bypass_wizard_prompts(self, wizard_next_button = '#hpid-wizard-next-button'):
        """
        This will navigate thru the Customer Prompts

        Args:
            wizard_next_button (str): selector for button
        """
        if self.is_visible(wizard_next_button):
            while not self.exists('#hpid-wizard-next-button.hp-disabled'):        
                log.debug("Press #hpid-wizard-next-button")
                self.press_virtual(wizard_next_button)
                time.sleep(1)
                # This code is a workaround for the prompt Location Not Configured as default Location is NONE and no choice available
                if self.exists('#hpid-wizard-next-button.hp-disabled') and self.exists('#hpid-wizard-finish-button.hp-disabled'):
                    if self.exists('#hpid-location-selection-unitedstates'):
                        self.press_screen('#hpid-location-selection-unitedstates')

        if not self.exists('#hpid-wizard-finish-button.hp-disabled') and self.is_visible('#hpid-wizard-finish-button'):
            log.debug("Press #hpid-wizard-finish-button")
            self.push_virtual_button('#hpid-wizard-finish-button')
            
    def connect(self):
        OmniUI.connected = True
        self.omni_service.Connect()

    def disconnect(self):
        OmniUI.connected = False
        self.omni_service.Disconnect()
        try:
            requests.get(
                "http://{}:{}/inspector/disconnect/1".format(self.ip_address, self.port), verify=False, timeout=3, allow_redirects=False)
        except:
                pass
    def close(self):
        OmniUI.connected = False
        self.omni_service.Disconnect()
        try:
            requests.get(
                "http://{}:{}/inspector/disconnect/1".format(self.ip_address, self.port), verify=False, timeout=3, allow_redirects=False)
        except:
                pass


    def check_state(self, selector, element_state):
        """
        checks the state of the element selected by the 
        selector. The element_state determines the type of 
        check suchs Exists, VisiblePartially
        """
        if element_state == ElementState.Exists:
            return self.exists(selector)
        elif element_state == ElementState.VisiblePartially:
            return self.is_visible(selector) and not self.exists(selector + ".hp-hidden")
        elif element_state == ElementState.VisibleCompletely:
            return self.is_completely_visible(selector) and not self.exists(selector + ".hp-hidden")
        elif element_state == ElementState.Useable:
            return self.is_completely_visible(selector) and not self.exists(selector + ".hp-hidden")
        else:
            raise ValueError("Unknown State {}".format(element_state))

    @omni_connection_handler
    def click(self, selector):
        """
        Clicks an element using the specified selector

        Args:
            selector (str): selector expression

        """
        self.omni_service.Click(selector)

    @omni_connection_handler
    def execute_omni_command(self, command):
        """
        This is raw command sent to omni

        Args:
            command (str): raw jquery command

        Returns:
            str: jquery response
        """
        return self.omni_service.ExecuteOmniTesterCommand(command)

    @omni_connection_handler
    def exists(self, selector):
        """
        Determines whether an element exists anywhere in the DOM.
        The element could be on a different tab or scrolled off 
        the screen and still exist.

        Args:
            selector (str): selector expression

        Returns:
            bool: True or False if the element exists
        """
        return self.omni_service.Exists(selector)

    def gesture(self, start_x, start_y, end_x, end_y, duration):
        """
        Perform a hold and then swipe gesture

        Args:
            start_x (int): The starting X coordinate.
            start_y (int): he starting Y coordinate
            end_x (int): The ending X coordinate
            end_y (int): The ending Y coordinate
            duration (int): The duration of the gesture, in milliseconds

        """
        path = "/test/touch/gesture"
        payload = {}
        payload['startx'] = start_x
        payload['starty'] = start_y
        payload['endx'] = end_x
        payload['endy'] = end_y
        payload['duration'] = duration
        full_path = "http://{}:{}{}".format(self.ip_address, self.port,path)
        response = requests.get(full_path, params=payload)
        if response.status_code == 200:
            return
        else:
            response.raise_for_status()

    @omni_connection_handler
    def get_all_ids_on_page(self):
        """
        Gets all IDs on the page.

        Args:

        Returns:
            [str]: list of ids

        """
        return list(self.omni_service.GetAllIdsOnPage())

    @omni_connection_handler
    def get_attribute_from_element(self, selector, attribute_name):
        """
        Gets the value of the specified attribute from an 
        element using the specified selector.

        Args:
            selector (str): selector expression
            attribute_name (str): the attribute name

        Returns:
            str: attribute value
        """
        return self.omni_service.GetAttributeFromElement(selector, attribute_name)

    @omni_connection_handler
    def get_children_ids(self, selector):
        """
        Gets the IDs of children of an element using the 
        specified selector.

        Args:
            selector (str): selector expression

        Returns:
            [str]: list of ids

        """
        return list(self.omni_service.GetChildrenIds(selector))

    @omni_connection_handler
    def get_count(self, selector):
        """
        Gets the number of elements matching the specified selector.

        Args:
            selector (str): selector expression

        Returns:
            int: the number of ids
        """
        return self.omni_service.GetCount(selector)

    @omni_connection_handler
    def get_css_from_element(self, selector, style_poperty_name):
        """
        Gets the value of the specified style property from an 
        element using the specified selector.

        Args:
            selector (str): selector expression
            style_poperty_name (str): the attribute name

        Returns:
            str: style property value
        """
        return self.omni_service.GetCssFromElement(selector, style_poperty_name)

    def get_count_hp_error(self):
        """
        get the number of hp errors

        Args:

        Returns:
            int: the number of errors
        """
        return self.get_count('.hp-listitem.hp-error')

    def get_count_hp_warning(self):
        """
        get the number of hp warnings
        
        Args:

        Returns:
            int: the number of warnings
        """
        return self.get_count('.hp-listitem.hp-warning')

    @omni_connection_handler
    def get_descendant_ids(self, selector):
        """
        Gets the IDs of descendants (recursively) of an element 
        using the specified selector.

        Args:
            selector (str): selector expression

        Returns:
            [str]: list of ids

        """
        return list(self.omni_service.GetDescendantIds(selector))

    @omni_connection_handler
    def get_ids(self, selector):
        """
        This will return the IDs of the selector. 

        Args:
            selector (str): selector expression

        Returns:
            [str]: list of ids
        """
        return list(self.omni_service.GetIds(selector))

    @omni_connection_handler
    def get_location(self, selector):
        """
        Gets location information for an element.

        Args:
            selector (str): selector expression

        Returns:
            ElementPosition: location of selector
        
        
        """
        return self.omni_service.GetLocation(selector)

    def get_message_center_error_messages(self):
        """
        This will return list of error messages

        Args:

        Returns:
            [str]: list of error messages
        """
        error_messages = []
        self.navigate_home()
        if self.is_message_error_button_present() or self.is_message_center_screen_present():
            if self.is_message_error_button_present():
                self.push_start_message_center_error_button()
            error_count = self.get_count('.hp-listitem.hp-error')
            if error_count > 0:
                for error in range(error_count):
                    selector = '.hp-listitem.hp-error:eq({})'.format(error)
                    err_msg_selector = '.hp-listitem.hp-error.hp-message-center-item:eq({})'.format(error)    
                    value = self.get_value(err_msg_selector, "innerText", Property.Property).strip()
                    err_msg = "Error[{0}]: {1}".format(error, value)
                    log.debug(err_msg)
                    error_messages.append(err_msg)
        return error_messages

    def get_message_center_warning_messages(self):
        """
        return a list of warning messages

        Returns:
            [str]: list of warning messages
        """
        warning_messages = []
        warning_count = self.get_count('.hp-listitem.hp-warning')
        if warning_count > 0:
            self.navigate_home()
            if not self.wait_for_home(wait_time=3):
                raise IOError("Omni home not present")  
            self.push_start_message_center_error_button()
        for warning in range(warning_count):
            selector = '.hp-listitem.hp-error:eq({})'.format(warning)
            if self.check_state(selector, ElementState.VisiblePartially):
                warning_msg_selector = '.hp-listitem.hp-warning.hp-message-center-item:eq({})'.format(warning)    
                value = self.get_value(warning_msg_selector, "innerText", Property.Property).strip()
                warning_msg = "Warning[{0}]: {1}".format(warning, value)
                warning_messages.append(warning_msg)
        return warning_messages
    
    @omni_connection_handler
    def get_property_from_element(self, selector, poperty_name):
        """
        Gets the value of the specified style property from an 
        element using the specified selector.

        Args:
            selector (str): selector expression
            poperty_name (str): the property name

        Returns:
            str: property value
        """
        return self.omni_service.GetPropertyFromElement(selector, poperty_name)

    def get_string(self, id):
        """
        get the string value from the id

        Args:
            id (int): the id number

        Returns:
            str: the string value from the id

        """
        return self.get_string_from_string_id(id)

    @omni_connection_handler
    def get_string_from_string_id(self, id):
        """
        Resolves a string ID to a display string for 
        the current locale. 

        Args:
            id (str): The string identifier

        Returns:
            str: The display string for the current locale.
        """
        return self.omni_service.GetStringFromStringId(id)

    def get_value(self, element_name, property_name, property_type):
        """
        Gets either Attribute, Property, or CSS element property 
        values

        Args:
            element_name (str): The element name
            property_name (str): The property name
            property_type (enum): Attribute, Css, or Property

        Returns:
            str: property value
        """
        if property_type == Property.Attribute:
            return self.get_attribute_from_element(element_name, property_name)
        elif property_type == Property.Css:
            return self.get_css_from_element(element_name, property_name)
        elif property_type == Property.Property:
            return self.get_property_from_element(element_name, property_name)
        else:
            raise ValueError("{} unknown property".format(property_type))

    def get_value_copies(self):
        """
        Get the number of copies

        Returns:
            str: the number of copies
        """
        return self.get_property_from_element('#hpid-homescreen-start-copies', 'value')

    def get_file_name(self):
        """
        Get the number of copies

        Returns:
            str: the number of copies
        """
        return self.get_property_from_element('#hpid-file-name-textbox', 'value')

    @omni_connection_handler
    def is_active(self, selector):
        """
        Determines whether any portion of an element is visible.

        Args:
            selector (str): selector expression

        Returns:
            bool: True or False if the element exists
        
        """
        return self.omni_service.IsActive(selector)

    def is_app_screen_present(self):
        """
        Determines if the app screen is present

        Returns:
            bool: True if app screen is present else False
        """
        return self.is_visible('.hp-app')

    @omni_connection_handler
    def is_completely_visible(self, selector):
        """
        Determines whether an element is completely visible.

        Args:
            selector (str): selector expression

        Returns:
            bool: True or False if the element exists
        
        """
        return self.omni_service.IsCompletelyVisible(selector)

    def is_homescreen_folder_present(self):
        """
        Determines if the home screen is present

        Returns:
            bool: True if home screen is present else False
        """
        return self.is_visible('.hp-homescreen-folder-view') or \
            self.is_completely_visible('.hp-homescreen-folder-view')

    def is_initial_wizard_screen_present(self):
        """
        Determines if the wizard screen is present

        Returns:
            bool: True if wizard screen is present else False
        """
        return self.is_visible('#hpid-initial-setup-wizard')

    def is_keyboard_present(self):
        """
        Determines if the keyboard screen is present

        Returns:
            bool: True if keyboard screen is present else False
        """
        return self.is_visible('#hpid-keypad')

    def is_message_center_present(self):
        """
        Determines if the message center is present

        Returns:
            bool: True if message center is present else False
        """
        return self.exists('.hp-button-message-center[type="Error"]')

    def is_message_center_screen_present(self):
        """
        Determines if the message center screen is present

        Returns:
            bool: True if message center screen is present else False
        """
        return self.is_visible('#hpid-message-center-screen')
    
    def is_message_button_present(self):
        """
        Determines if the message center button is present

        Returns:
            bool: True if message center button is present else False
        """
        return self.is_visible('.hp-button-message-center')
        
    def is_message_error_button_present(self):
        """
        Determines if the message center error button is present

        Returns:
            bool: True if message center error button is present else False
        """
        return self.is_visible('.hp-button-message-center[type="Error"]')
        
    def is_message_warning_button_present(self):
        """
        Determines if the message center warning button is present

        Returns:
            bool: True if message center warning button is present else False
        """
        return self.is_visible('.hp-button-message-center[type="Warning"]')


    def is_omni_service_available(self, time_to_wait=30, sleep_time=.5):
        """
        It will wait for Omni service to be available. 
        Args:
            time_to_wait (int): how long to wait
            sleep_time (float): loop delay

        Returns:
            bool: True if service available else False
        """
        start_time = time.time()
        elapsed_time = time.time() - start_time
        while elapsed_time < time_to_wait:
            log.info("Waiting for OMNI Service {}".format(int(time_to_wait - elapsed_time)))
            try:
                self.is_homescreen_folder_present()
                return True
            except:
                time.sleep(sleep_time)
                elapsed_time = time.time() - start_time
        return False

    def is_popup_screen_present(self):
        """
        Determines if the popup screen is present

        Returns:
            bool: True if popup screen is present else False
        """
        return self.exists(".hp-popup-modal-overlay")

    def is_virtual_keyboard_present(self):
        """
        Determines if the virtual keyboard is present

        Returns:
            bool: True if virtual keyboard is present else False
        """
        return self.is_visible('#hpid-keyboard')

    @omni_connection_handler
    def is_visible(self, selector):
        """
        Determines whether any portion of an element is visible.

        Args:
            selector (str): selector expression

        Returns:
            bool: True or False if the element exists
        
        """
        return self.omni_service.IsVisible(selector)

    def navigate_home(self):
        """
        Navigate Home it will try numerous actions to 
        navigate home
        """
        if self.is_initial_wizard_screen_present():
            self.bypass_wizard_prompts()
        self.press_key(PanelButton.Home)
        #time.sleep(.1)
        #self.press_key(PanelButton.Home)

    def press_key(self, key):
        """
        Press Hard Key 

        Args:
            key (str): The type of key
        """
        client = ControlPanelQualificationServiceClient(self.ip_address)
        try:
            client.PressHardKey(key)
            client.Close()
        except:
            log.exception("{} key failed".format(key))
            client.Abort()

    def press_panel_home(self):
        """
        use press_key to press PanelButton.Home
        """
        self.press_key(PanelButton.Home)
        
    def press_screen(self, x, y):
        """
        Virtual tap at x and y locations
        Args:
            x (int): x location
            y (int): y location
        """
        self.tap(x,y,1,100)

    def press_virtual(self, selector):
        """
        Tap the selector 

        Args:
            selector (str): selector 
        """
        if self.check_state(selector, ElementState.Useable):
            # calculate location to tap
            location = self.get_location(selector)
            x_loc, y_loc = location.Right - 1, location.Bottom - 1
            if location.CenterVisible:
                x_loc, y_loc = location.CenterX, location.CenterY
            elif location.TopLeftVisible:
                x_loc, y_loc = location.Left + 1, location.Top + 1
            elif location.TopRightVisible:
                x_loc, y_loc = location.Right - 1, location.Top + 1
            elif location.BottomLeftVisible:
                x_loc, y_loc = location.Left + 1, location.Bottom - 1
            
            # Perform Tap
            self.tap(x=x_loc, y=y_loc, taps=1, interval=100)
        else:
            if self.check_state(selector, ElementState.Exists):
                raise IOError("The element specified by selector {} is not useable.".format(selector))
            else:
                raise IOError("The element specified by selector {} does not exist.".format(selector))

    def push_keypad_backspace(self):
        """
        Virtual tap on (10 key) keypad backspace
        """
        self.push_virtual_button('#hpid-keypad-key-backspace')

    def push_keyboard_backspace(self):
        """
        Virtual tap on the full keyboard (not the 10 key) backspace
        """
        self.push_virtual_button('#hpid-keyboard-key-backspace')

    def push_keypad_close(self):
        """
        Virtual tap on keypad close
        """
        self.push_virtual_button('#hpid-keypad-key-close')

    def push_keypad_number(self, number):
        """
        Virtual tap on keypad number

        Args:
            number (int): The number to tap
        """
        t = int(number)
        if t < 0 or t > 10:
            raise Exception("Illegal keypad number {} only 0 -9 are allowed".format(number))

        selector = ".hpid-keypad-key-" + str(number)
        self.push_virtual_button(selector)
    
    def push_reset_button(self):
        """
        Virtual tap on  Reset Button

        """
        self.push_virtual_button('#hpid-button-reset')

    def push_start_copies_button(self):
        """
        Virtual tap on copies button
        """
        self.push_virtual_button('#hpid-homescreen-start-copies')


    def push_file_name_box(self):
        """
        Virtual tap on copies button
        """
        self.push_virtual_button('#hpid-file-name-textbox')

    def push_scan_to_network_button(self):
        """
        Virtual tap on copies button
        """
        self.push_virtual_button('#hpid-networkFolder-homescreen-button')

    def push_start_start_button(self):
        """
        Virtual start start button
        """
        if self.check_state('#hpid-button-homescreen-start',ElementState.VisiblePartially):
            offsetLeft = self.get_value('#hpid-button-homescreen-start','offsetLeft',Property.Property)
            offsetTop = self.get_value('#hpid-button-homescreen-start','offsetTop',Property.Property)
            self.press_screen(int(offsetLeft),int(offsetTop))
        else:
            raise Exception('Start button not on screen')

    def push_start_message_center_error_button(self):
        """
        Virtual tap message center error button
        """
        self.push_virtual_button('.hp-button-message-center[type="Error"]')

    def push_start_message_center_exit_button(self):
        """
        Virtual tap message center exit button
        """
        self.push_virtual_button('#hpid-message-center-exit-button')

    def push_start_message_center_warning_button(self):
        """
        Virtual tap message center warning button
        """
        self.push_virtual_button('.hp-button-message-center[type=Warning]')  

    def push_wizard_finish_button(self):
        """
        Virtual tap wizard finish button
        """
        self.push_virtual_button('#hpid-wizard-next-button')
    
    def push_wizard_next_button(self):
        """
        Virtual tap wizard next button
        """
        self.push_virtual_button('#hpid-wizard-finish-button')

    def push_virtual_button(self, selector):
        """
        The virtual tap on selector

        Args:
            selector (str): selector 
        """
        self.press_virtual(selector)

    def scroll_press(self, selector):
        """
        Scroll to selector and virtual tap 
        """
        self.scroll_to(selector)
        self.press_virtual(selector)

    @omni_connection_handler
    def scroll_to(self, selector):
        """
        Scrolls to an element using the specified selector.

        Args:
            selector (str): selector expression

        """
        self.omni_service.Click(selector)

    @omni_connection_handler
    def set_slider_value(self, selector, value):
        """
        Resolves a string ID to a display string for the current locale.

        Args:
            selector (str): selector expression
            value (int): The slider value

        """
        self.omni_service.SetSliderValue(selector, value)

    def swipe_screen(self, x_start, y_start, x_end, y_end, duration=20):
        """
        Swipe Screen starting (x_start, y_start) to (x_end, y_end) for duration
        time

        Args:
            x_start (int): x start location
            y_start (int): t start location
            x_end (int): x end location
            y_end (int): y end location
            duration (int): time in miliseconds for swipe
        """
        self.gesture(x_start, y_start, x_end, y_end, duration)

    def tap(self, x, y, taps, interval):
        """
        Taps the control panel the specified number of times at the specified location.
        Args:
            x (int): The X coordinate.
            y (int): The Y coordinate.
            taps (int): The number of taps
            interval (int): The interval between taps, in milliseconds.

        """
        path = "/test/touch/tap"
        payload = {}
        payload['x'] = x
        payload['y'] = y
        payload['taps'] = taps
        payload['interval'] = interval
        full_path = "http://{}:{}{}".format(self.ip_address, self.port,path)
        response = requests.get(full_path, params=payload)
        if response.status_code == 200:
            return
        else:
            response.raise_for_status()

    @omni_connection_handler
    def type_on_numerical_keypad(self, text):
        """
         Types the specified text on the numeric keypad.
         Args:
            text (str): The text to type
        """
        self.omni_service.TypeOnNumericKeypad(text)

    @omni_connection_handler
    def type_on_virtual_keyboard(self, text, continue_on_error=True):
        """
         Types the specified text on the virtual keyboard.

         ExecuteOmniTesterCommand("typeOnNumericKeypad({0})".format(text))

         Args:
            text (str): The text to type
            continue_on_error (bool): ontinue typing if a character cannot be 
                found on the keyboard.

        """
        self.omni_service.TypeOnVirtualKeyboard(text, continue_on_error)


    def wait_for_home(self, wait_time=5, delay_time=0.5):
        """
        wait for home screen to appear

        Args:
            wait_time (float): how long to wait
            delay_time (float): how much delay between loops

        Returns:
            bool: True if home screen is present else False
        """
        start = time.time()
        while ((time.time() - start) < int(wait_time)):
            if self.is_homescreen_folder_present():
                return True 
            time.sleep(delay_time)
        return False

    def wait_for_value(self, element_name, property_name,expected_value, property_type, wait_time, delay_time=0.5):
        """
        Wait for a specific expected_value for wait_time seconds

        Args:
            element_name (str): The element name
            property_name (str): The property name
            expected_value (str): expected value 
            property_type (Property): Attribute, Property, Css
            wait_time (float): how long to wait for expected_value
            delay_time (float): delay time between loops

        Returns:
            bool: True if expected_value is received else False
        """
        start = time.time()
        while ((time.time() - start) < int(wait_time)):
            if expected_value == self.get_value(element_name, property_name,property_type):
                return True 
            time.sleep(delay_time)
        return False

    def wait_for_state(self, element_name, element_state,wait_time, delay_time=0.5):
        """
        wait for expected element_state for wait_time seconds

        Args:
            element_name (str): The element name
            element_state (str): expected state value 
            wait_time (float): how long to wait for expected_value
            delay_time (float): delay time between loops

        Returns:
            bool: True if element_state is received else False
        """
        start = time.time()
        while ((time.time() - start) < int(wait_time)):
            if self.check_state(element_name, element_state):
                return True
            time.sleep(0.5)
        return False           

    def enable_omni(self, adminPassword=""):
        log.info("enabling omni")
        omni = omni_enable()
        omni.Main(self.ip_address,adminPassword)

