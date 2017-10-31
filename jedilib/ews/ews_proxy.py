"""
Ews.py
"""
__version__ = '$Revision: 48177 $'
__author__  = '$Author: dfernandez $'
__date__    = '$Date: 2016-06-20 08:18:39 -0600 (Mon, 20 Jun 2016) $'

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import time
import socket

from .wifi_direct import WifiDirect, WifiDirectCreator

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# 3rd Party modules
# =============================================================================
import requests
from bs4 import BeautifulSoup
          

# =============================================================================
# Globals and Definitions
# =============================================================================
EWS_IPADDRESS = ""
HTTP_SCHEME = "http"

SCAN_CONFIG_DATA = {"IP_SLP":"on","M_DNS":"on","M_IPV4":"on","IP_9100":"on","AirPrint":"on","IP_LPD":"on","IP_IPP":"on","IP_IPPS":"on","XML_Ser":"on","Ws_Discovery":"on","LLMNR":"on","IP_WSPrint":"on","eSCLNetwork":"on","SecureeSCL":"on","EnableWINSPort":"on","WINSRegistration":"on","TftpFilePullDown":"on","LinkSettings":"ZAUTOS","IP_LAA":"9457A5CD86C8","SyslogType":"LPR","HttpTimeOut":"15","networkConn":"on","Raw_port1":"","Raw_port2":"","priorityService":"2","CertPullPrint":"on","Username":"","Password":"","VerifyPassword":"","Apply":"Apply"}

SECURITY_CONFIG_DATA = {"isSet":"False","newPassword":"","verifyPassword":"","ServicePin":"","VerifyServicePin":"","dssPassword":"","dssVerifyPassword":"","displayPrintPage":"on","displayJobLogPage":"on","defaultSessionTimeout":"30","enableRemoteUserAutoCapture":"on","NewPjlPassword":"","VerifyNewPjlPassword":"","EnableDeviceAccess":"on","IsPrintPathEnabled":"on","LegacyEncryptionAlgorithm":"on","PJLFileSystemAccess":"on","PostScriptFileSystemAccess":"on","disableDirectConnect":"on","UsbPortsEnabled":"on","FormButtonSubmit":"Apply"}

PASS = 1
FAIL = 0

# =============================================================================
# classes
# =============================================================================
# =============================================================================
# Classes
# =============================================================================
class FailToDisableWebCommunicationEncryptionException(Exception):
    pass
    
class InformationLog(object):
    def __init__(self):
        self.number = ""
        self.date_and_time = ""
        self.cycle = ""
        self.event = ""
        self.firmware = ""
        self.description = ""
        self.consecutive_repeats = ""
    
    def __str__(self):
        rep = self.number + " " + self.date_and_time + " " + self.cycle \
            + " " + self.event + " " + self.firmware + " " + self.description \
            + " " + self.consecutiveRepeats

class ConnectedClients(object):
    def __init__(self,mac_addr, ip_addr):
        self.MacAddress = mac_addr
        self.IPAddress = ip_addr
 

        
class Ews(object):
    """
    EWS Proxy web scrapes values from HTML provided by the EWS server. 
    """
    def __init__(self,ip_address,http_scheme="http"):
        """
        The Constructor to initialize the object

        Args:

        ip_address (str): ip_address the IP address of printer with a default of 10.1.1.100
        http_scheme (str): http_scheme either http or https
        """    
        self.ip_address = ip_address
        self.http_scheme = http_scheme  

    def enable_escl(self, scan_config_data = SCAN_CONFIG_DATA, security_config_data = SECURITY_CONFIG_DATA):
        """
        This will enable support for eSCL scanning. It will perform two http POSTs to enable this support. It will
        post on https://<IP Address>/application_param.htm/config and https://<IP ADDRESS>/hp/device/GeneralSecurity/Save 

        Args:
        scan_config_data (dict): dictionary HTTP POST data for https://<IP Address>/application_param.htm/config
            if not given will use SCAN_CONFIG_DATA dictionary
        security_config_data (dict): dictionary HTTP POST data for https://<IP ADDRESS>/hp/device/GeneralSecurity/Save
            if not given will use SECURITY_CONFIG_DATA dictionary

        Returns:
            
        Raises:
            HTTPError: If the status code for one of the HTTP POSTs is not 200
        """    
        url_get_scan_config = 'https://{}/application_param.htm'.format(self.ip_address) 
        url_scan_config = 'https://{}/application_param.htm/config'.format(self.ip_address) 
        url_security_config = 'https://{}/hp/device/GeneralSecurity/Save'.format(self.ip_address)
        
        r = requests.get(url_get_scan_config, verify=False)
        if r.status_code != 200:
            raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_get_scan_config, r.status_code), response = r)
        soup = BeautifulSoup(r.text, 'html5lib')
        item = soup.find(lambda tag: tag.has_attr('id') and tag['id'] == "IP_LAA")

        scan_config_data["IP_LAA"] = item["value"]
        r = requests.post(url_scan_config, data = scan_config_data, verify=False)
        if r.status_code != 200:
            raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_scan_config, r.status_code), response = r)
        

        r = requests.post(url_security_config, data = security_config_data, verify=False)
        if r.status_code != 200:
            raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_security_config, r.status_code), response = r)

    def get_wifi_direct_page(self, url_open_time_out = 30, url_path = "/wireless_direct.htm"): #"/hp/jetdirect"):
        """
        Gets the Wifi Direct Printing page

        Args:
            url_open_time_out (int): The timeout time to get page

            url_path (str): the path to the page

        Returns:
            WifiDirect: WifiDirect object that contains information about page

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """
        url = self.http_scheme + "://" + self.ip_address + url_path
        log.info("EWS Get Wifi Direct Printing Page Values at url: " + url)        
        text = self._urlopen(url,url_open_time_out)
        soup = BeautifulSoup(text,  "html5lib")
        return WifiDirectCreator.CreateWifiDirect(soup)
        
    def get_staple_stacker_installed(self, url_open_time_out = 30, url_path = "/hp/device/OpenFromUsb/Index"): 
        """
        See's if the staple stacker shows up in the Copy\Print menu.
        If it does then we assume the staple stacker in installed

        Args:
            url_open_time_out (int): The timeout time to get page
            url_path (str): the path to the page

        Returns:
            True or False

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """
        url = self.http_scheme + "://" + self.ip_address + url_path
        log.info("Get Staple-Stacker Menu at url: " + url) 
        text = self._urlopen(url,url_open_time_out)
        soup = BeautifulSoup(text,"lxml")
        item = soup.find(lambda tag: tag.has_attr("id") and tag["id"] == "StaplerStacker")
        
        return item
        
    def get_ble_beacon_enabled(self, url_open_time_out = 30, url_path = "/hp/device/GeneralSecurity/Index"): 
        """
        Gets the Bluetooth HP Beacon Enabled page

        Args:
            url_open_time_out (int): The timeout time to get page
            url_path (str): the path to the page

        Returns:
            True or False

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """
        url = self.http_scheme + "://" + self.ip_address + url_path
        log.info("EWS Get BLE Printing Page Values at url: " + url) 
        check = self._check_for_attribute(url,"BleBeaconSelect_2")
        return check
        
    def set_ble_to_enabled(self, url_open_time_out = 30): 
        """
        Sets BLE HP Beacon on printer to enabled 

        Args:
            url_open_time_out (int): The timeout time to get page

        Returns:
            none

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """
        url_security_index = 'http://{}/hp/device/GeneralSecurity/Index'.format(
            self.ip_address)
        url_security_config = 'http://{}/hp/device/GeneralSecurity/Save'.format(
            self.ip_address)
        security_config_data = SECURITY_CONFIG_DATA.copy()
        security_config_data["BleEnabled"] = "1"
        security_config_data["BleBeaconType"] = "0"
        security_config_data["BleBeaconSelect"] = "HPPrintProximityBeacon"

        s = requests.Session()
        r_temp = s.get(url_security_index, verify=False)
        headers = {'Referer': url_security_index}
        r = s.post(url_security_config,
                   data=security_config_data,
                   verify=False,
                   headers=headers)
        if r.status_code != 200:
            raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(
                url_security_config, r.status_code), response=r)
    
    def set_ble_to_disabled(self, url_open_time_out = 30): 
        """
        Sets BLE HP Beacon on printer to disabled

        Args:
            url_open_time_out (int): The timeout time to get page
        Returns:
            none

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """
        url_security_index = 'http://{}/hp/device/GeneralSecurity/Index'.format(
            self.ip_address)
        url_security_config = 'http://{}/hp/device/GeneralSecurity/Save'.format(
            self.ip_address)
        security_config_data = SECURITY_CONFIG_DATA.copy()
        security_config_data["BleEnabled"] = "2"
        security_config_data["BleBeaconType"] = "0"
        security_config_data["BleBeaconSelect"] = "Disabled"

        s = requests.Session()
        r_temp = s.get(url_security_index, verify=False)
        headers = {'Referer': url_security_index}
        r = s.post(url_security_config,
                          data=security_config_data, 
                          verify=False, 
                          headers = headers)
        if r.status_code != 200:
            raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(
                url_security_config, r.status_code), response=r)
  
    def get_config_page_values(self, url_open_time_out = 30):
        """
        This returns a dictionary with the EWS configuration page values

        Args:
            url_open_time_out (int): the timeout to get configuration page

        Returns:
            dict: configuration page key/value pairs

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """    
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/InternalPages/Index?id=ConfigurationPage"
        log.debug("EWS Get Config Page Values at url: " + url)        
        log.info("EWS Waiting to Open Config Page Url")    
        text = self._urlopen(url,url_open_time_out)
        soup = BeautifulSoup(text, "html5lib")
        items = soup.findAll(lambda tag: tag.has_attr('id') 
            and (tag.name.find("strong")>=0 or tag.name.find('td')>=0)) 
        
        elements = {}
        for item in items:
            key = item['id']
            value = item.text
            elements[key] = value
        
        #Duplexor
        elements['DuplexUnit'] = "NotInstalled"
        tItems = soup.findAll(lambda tag: tag.has_attr('id') 
            and (tag['id'].find('DuplexUnit') >= 0))
        if len(tItems) > 0:
            elements['DuplexUnit'] = "Installed"
        return elements
        
        
    def get_security_page_values(self, url_open_time_out = 30):
        """
        This returns a dictionary with the EWS security page values

        Args:
            url_open_time_out (int): the timeout to get configuration page

        Returns:
            dict: security page key/value pairs

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page

        """    
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/GeneralSecurity/Index"
        log.debug("EWS Get Security Page Values at url: " + url)
        log.info("EWS Waiting to Open Security Page Url")
        text = self._urlopen(url,url_open_time_out)
        soup = BeautifulSoup(text, "html5lib")
        items = soup.findAll(lambda tag: tag.has_attr('id') \
            and (tag.name.find("strong")>=0 or tag.name.find('td')>=0))
        
        elements = {}
        for item in items:
            key = item['id']
            value = item.text
            elements[key] = value.strip()
        return elements
        
    
    def get_date_and_time_values(self):
        """
        This returns a dictionary with the EWS Date and Time values

        Args:

        Returns:
            dict: Date and Time key/value pairs

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """    
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/RealTimeClock/Index"
        text = self._urlopen(url,10)
        soup = BeautifulSoup(text,"html5lib")
        items = soup.findAll(lambda tag: tag.has_attr('id') and 'value' in tag and (tag.name.find("input") >= 0) )

        elements = {}
        for item in items:
            key = item['id']
            value = item['value']
            elements[key] = value

        #need to get month, which is the "selected" input
        #items = soup.findAll(lambda tag: (tag.has_key('id') and (tag.name.find("select") >= 0) ) )
        return elements

    def get_event_log_page_values(self):
        """
        This returns a list of dictionaries of the event log entries from
        the EWS EventLogPage. The list index will be row entry and the dictionary
        key will be the column entry such as l[rowNum][ColumnHeaderName]. An example
        l = GetJedEventLogPageValues()
        firmwareRevision = l[0]["Firmware"]

        Args:

        Returns:
            dict: event entries key/value pairs

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page
        """    
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/InternalPages/Index?id=EventLogPage"
        stream = self._urlopen(url,10)
        soup = BeautifulSoup(stream, "lxml")
        table = soup.find("table")
        
        return self._ParseTableForListOfDicts(table)
        
    
    def get_information_log_page_values(self):
        """
        This returns a list of dictionaries of the event log entries from
        the EWS Information log. The list index will be row entry and the dictionary
        key will be the column entry such as l[rowNum][ColumnHeaderName]. 

        Args:

        Returns:
            dict: info entries key/value pairs

        Raises:
            requests.HTTPError: for unsuccessful HTTP GET on page

        """    
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/ReportsAndTests/Index"
        text = self._urlopen(url,10)
        soup = BeautifulSoup(text, "html5lib")
        t = soup.find(text=lambda text:text.find("Information Log")>= 0)
        inputTag = t.parent.find("input")
        id = inputTag["value"]
        
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/ReportsAndTestsView/Index?id=" + id +"&StepBackController=ReportsAndTests&StepBackAction=Edit"
        text = self._urlopen(url,10)
        soup = BeautifulSoup(text, "html5lib")
        table = soup.find("table")
        
        return self._ParseTableForListOfDicts(table)
    
    def save_cp_snapshot_to_file(self,imageFilePath):
        """
        This takes a screenshot of control panel and save the image
        to the imageFilePath

        Args:
			imageFilePath (str): The full file path where the image will be saved.
				An example c:\HpCustom\Data\ScreenShot.jpg

        Returns:

        Raises:
		
        """    
        
        s = requests.Session()
        url_cp_index = self.http_scheme + "://" + self.ip_address + "/hp/device/ControlPanelSnapshot/Index"
        s.get(url_cp_index, verify = False)
        headers = {'Referer': url_cp_index}
        url_cp_image = self.http_scheme + "://" + self.ip_address + "/hp/device/ControlPanelSnapshot/Image"
        r = s.get(url_cp_image, verify = False, stream = True, headers = headers)   
        if r.status_code == requests.codes.ok:
            with open(imageFilePath, 'wb') as f:
                import shutil
                shutil.copyfileobj(r.raw, f)
        
    def print_from_usb(self, enable = True):
        """
		Enables the printer to be able to print from a USB device.
		
		Args:
			enable (bool): default to True if you use this function it's
				assumed that you want to turn on the service. 
		Returns:
        """
		
        s = requests.Session()
        url_index =  self.http_scheme + "://" + self.ip_address + "/hp/device/OpenFromUsb/Index"
        s.get(url_index, verify = False)
        headers = {'Referer': url_index}
        url =  self.http_scheme + "://" + self.ip_address + "/hp/device/OpenFromUsb/Save"
        value = "on" if enable else "off"
        data = {"EnableOpenFromUsb": value, "FormButtonSubmit":"Apply"}
        r = s.post(url, verify=False, data = data, headers = headers)
        r.status_code
        
    def uncheck_encrypt_all_web_communication(self, enable = False):
        """
        This function will verify that the setting is unchecked.
        If it is checked, then it will uncheck and post the ews page.
        Args:
            enable (bool): default to False if you use this function it's
            assumed that you want to turn off the encryption. 
        raises:
            FailToDisableWebCommunicationEncryptionException
        Returns:
        """
        log.debug("Checking Status of Encrypt All Web Communication")
        s = requests.Session()
        url_get = self.http_scheme + "://" + self.ip_address + "/websecurity/http_mgmt.html"
        encrypt_status = self._check_for_attribute(url_get, "encryptall")
        log.debug("encrypt_status = {}".format(encrypt_status))
        loop = 0
        if not enable:
            while encrypt_status and (loop<2):
                log.debug("Uncheck option for Encrypt All Web Communication")
                data = {"Apply":"Apply", "Hide":"0"}
                url_post = url_get + "/config"
                headers = {'Referer': url_post}
                r = s.post(url_post, verify=False, data = data, headers = headers)
                encrypt_status = self._check_for_attribute(url_get, "encryptall")
                log.debug("encrypt_status = {}".format(encrypt_status))
                loop +=1
            
        if encrypt_status and not enable:
            err_msg = "\nFail to turn off the encryption for all web communication\n\n\t Status Code : {}".format(r.status_code)
            raise FailToDisableWebCommunicationEncryptionException(err_msg)
        
    def wait_for_ews_ready(self, max_time, loop_delay = 10):
        """
        This will loop on HTTP GET on the configuration page for max_time 
        seconds

        Args:
			max_time (int): the upper limit for the time elapsed to get config page
			lop_delay (int): loop_delay is the time to sleep between loops default 1 second

        Returns:
            bool: True successful getting config page False not successful
        """    
        if type(max_time) is str:
            max_time = int(max_time)
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/InternalPages/Index?id=ConfigurationPage"
        log.debug("EWS Wait For Url Ready for " + url)        
        receivedHttpFlag = True
        start = time.time()
        log.info("EWS Waiting For Url Ready: LoopDelay " + str(loop_delay) + " sec")
        text = ""
        try:
            text = self._urlopen(url, max_time)
        except:
            receivedHttpFlag = False
        return receivedHttpFlag, text

    def wait_for_ews_config_ready(self, max_time, loop_delay = 10):
        """
        This will loop on HTTP GET on the configuration page is successfull. It
        will perform operation for max_time seconds.  It will return a tuple 
        (succesfull flag, dictionary of key/values)

        Args:
        max_time (int): the upper limit for the time elapsed
        
        lop_delay (int): loop_delay is the time to sleep between loops default is 10 seconds

        Returns:
            bool, dict: True successful getting config page False not successful and dictionary 
                of configu key/values
        """    
        if type(max_time) is str:
            max_time = int(max_time)
        url = self.http_scheme + "://" + self.ip_address + "/hp/device/InternalPages/Index?id=ConfigurationPage"
        log.debug("EWS Wait For Url Ready for " + url)        
        receivedHttpFlag = False
        start = time.time()
        log.info("EWS Waiting For Url Ready: LoopDelay " + str(loop_delay) + " sec")
        elements = {}    
        while ((time.time() - start) < max_time):
            try:
                text = self._urlopen(url, max_time)
                soup = BeautifulSoup(text,  "lxml")
                items = soup.findAll(lambda tag: tag.has_attr('id') and (tag.name.find("strong")>=0 or tag.name.find('td')>=0)) 
                for item in items:
                    key = item['id']
                    value = item.text
                    elements[key] = value
                elements['DuplexUnit'] = "NotInstalled"
                tItems = soup.findAll(lambda tag: tag.has_attr('id') 
                    and (tag['id'].find('DuplexUnit') >= 0))
                if len(tItems) > 0:
                    elements['DuplexUnit'] = "Installed"
                receivedHttpFlag = True
                break;
            except Exception as ex:
                log.debug("EWS Url Open Exception after time_out of " + str(loop_delay) + " sec")
                print(ex)
                time.sleep(int(loop_delay))
            log.info("EWS Waiting For Url Ready: " + str(int(time.time() - start)) + " of " + str(max_time))    
                
        return receivedHttpFlag, elements
        
    def wait_for_ews_port_ready(self, max_time, port = 80, loop_delay = 10):
        """
        This will loop on socket connect for time seconds until we have success.

        Args:
        max_time (int): the upper limit for the time elapsed to open socket connection
        
        lop_delay (int): loop_delay is the time to sleep between loops

        Returns:
            bool: True successful opening socket False not successful
        """    
        if type(max_time) is str:
            max_time = int(max_time)
        log.debug("EWS Wait For Port Ready for " + str(port))        
        start = time.time()
        log.info("EWS Waiting For Port " + str(port) + " Ready: LoopDelay " + str(loop_delay) + " sec")    
        while ((time.time() - start) < max_time):
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                if s.connect_ex((self.ip_address,int(port))) == 0:
                    s.close()
                    return True
                s.close()
            except:
                log.debug("EWS Port Open " + str(port) + " Exception after time_out of " + str(loop_delay) + " sec")
            time.sleep(int(loop_delay))
            log.info("EWS Waiting For Port " + str(port) + ": " + str(int(time.time() - start)) + " of " + str(max_time)+ " sec")    
                
        return False
    
    def _check_for_attribute(self, url, attr_find_value, attr_find = 'id', attr_check = 'checked'):
        """
        This is a private function that takes a url and checks the url
        for a specific attribute. If it finds that attribute it checks 
        the disctionary returned for another attribute.

        Args:
            url(str): Url to open and get soup back for
            attr_find_value (str): the value for the attribute your searching for
            attr_find (str): attribute to get initial dictionary  
            attr_check (str): searches dictionary returned for another attribute

        Returns:
            bool: True if attr_check exists in found dictionary else False
        """
        text = self._urlopen(url,10)
        soup = BeautifulSoup(text,"lxml")
        item = soup.find(lambda tag: tag.has_attr(attr_find) and tag[attr_find] == attr_find_value)
        log.debug("Checking attributes : {}".format(item.attrs))
        
        if item.has_attr(attr_check):
            encrypt_status = True
            log.debug("It is checked.")
            return True
        else:
            log.debug("It is not checked.")
            return False
    
    def _ParseTableForListOfDicts(self, table):
        """
        This will loop thru HTML Table to product dictionaries

        Args:
            table (BeautifulSoup.Table): This is from BeautifulSoup Table

        Returns:
            dict: breaks the table into dictionary of dictionary

        """
        headers = table.findAll("th")
        rows = table.findAll("tr")
        elements = []
        for row in rows:
            values = {}
            index = 0
            cells = row.findAll("td")
            if len(cells) == 0:
                continue
            for cell in cells:
                values[headers[index].text] = cell.text
                index = index + 1
            elements.append(values)
        
        return elements

    def _urlopen(self, url,url_open_time_out = 20):
        """
        helper method to open a request page and return the response.text

        Args:
        url (str): The url endpoint to perform a requests.get

        url_open_time_out (int): The open timeout for the requests.get

        Returns:
            str: response.text html body

        Raises:
            requests.HTTPError: If the status code is not 200 for the HTTP GET
            Exception: for unknown expcetion
        """
        start = time.time()
        maxTime = 10  
        while True:
            try:
                r = requests.get(url, verify = False)
                log.debug("HTTP status_code = {}".format(r.status_code))
                if r.status_code == requests.codes.ok:
                    return r.text
                else:
                    raise requests.HTTPError("{} failed to retrieve".format(url), response = r) 
            except:
                if ((time.time() - start) > maxTime):
                    raise Exception("EWS URL open Failed Exception after time_out of " + str(maxTime) + " sec")
            time.sleep(1)
# =============================================================================
# Globals and Definitions
# =============================================================================
ConfigAndFirmwareVarBasicList = [
    "SerialNumber",
    "FormatterNumber",
    "ProductName",
    "DeviceName",
    "ModelNumber",
    "FirmwareRevision",
    "DCControlVersion",
    "DefaultPaperSize",
    ]
    
# =============================================================================
# Public Functions
# =============================================================================

# =============================================================================
# Private Functions
# =============================================================================


#ServicePointManager.ServerCertificateValidationCallback = _CertChecker;

#==============================================================================
# Test
#==============================================================================
if __name__ == '__main__':
    # Peform test initialization sequence
    # could perform test without Falcon here
    # import another File that performs the same test
    sys.stdout.write("Enter IP Address -> ")
    lin = sys.stdin.readline()
    EWS_IPADDRESS = lin[:-1]
    pass
