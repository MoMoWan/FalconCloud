"""
eSCL.py This will contain eSCL information 
"""
__version__ = '$Revision: 48177 $'
__author__  = '$Author: dfernandez $'
__date__    = '$Date: 2016-06-20 08:18:39 -0600 (Mon, 20 Jun 2016) $'

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import re
import time
import collections
import shutil
from enum import Enum

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
SCANNER_TEMPLATE_TICKET = '''<?xml version="1.0" encoding="UTF-8"?><ScanSettings xmlns="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.hp.com/imaging/escl/2011/05/03 Scan Schema - 0.26.xsd">...<Version xmlns="http://www.pwg.org/schemas/2010/12/sm">2.5</Version><ScanRegions xmlns="http://www.pwg.org/schemas/2010/12/sm" xmlns:n0="http://www.pwg.org/schemas/2010/12/sm" n0:MustHonor="false"><ScanRegion><Height></Height><Width></Width><XOffset></XOffset><YOffset></YOffset><ContentRegionUnits>escl:ThreeHundredthsOfInches</ContentRegionUnits></ScanRegion></ScanRegions><XResolution></XResolution><YResolution></YResolution><CompressionFactor></CompressionFactor><Brightness></Brightness><Contrast></Contrast><AutoCrop></AutoCrop><Duplex></Duplex><DocumentFormatExt></DocumentFormatExt><ColorMode></ColorMode><InputSource xmlns="http://www.pwg.org/schemas/2010/12/sm"></InputSource><FeedDirection></FeedDirection></ScanSettings>'''

SCAN_CONFIG_DATA = {"IP_SLP":"on","M_DNS":"on","M_IPV4":"on","IP_9100":"on","AirPrint":"on","IP_LPD":"on","IP_IPP":"on","IP_IPPS":"on","XML_Ser":"on","Ws_Discovery":"on","LLMNR":"on","IP_WSPrint":"on","eSCLNetwork":"on","SecureeSCL":"on","EnableWINSPort":"on","WINSRegistration":"on","TftpFilePullDown":"on","LinkSettings":"ZAUTOS","IP_LAA":"9457A5CD86C8","SyslogType":"LPR","HttpTimeOut":"15","networkConn":"on","Raw_port1":"","Raw_port2":"","priorityService":"2","CertPullPrint":"on","Username":"","Password":"","VerifyPassword":"","Apply":"Apply"}

SECURITY_CONFIG_DATA = {"isSet":"False","newPassword":"","verifyPassword":"","ServicePin":"","VerifyServicePin":"","dssPassword":"","dssVerifyPassword":"","displayPrintPage":"on","displayJobLogPage":"on","defaultSessionTimeout":"30","enableRemoteUserAutoCapture":"on","NewPjlPassword":"","VerifyNewPjlPassword":"","EnableDeviceAccess":"on","IsPrintPathEnabled":"on","LegacyEncryptionAlgorithm":"on","BleEnabled":"1","BleBeaconType":"0","BleBeaconSelect":"Disabled","PJLFileSystemAccess":"on","PostScriptFileSystemAccess":"on","disableDirectConnect":"on","UsbPortsEnabled":"on","FormButtonSubmit":"Apply"}

ScannerStatus = collections.namedtuple('ScannerStatus', 'state adf_state')

# =============================================================================
# classes
# =============================================================================

class InvalidTicketFormat(requests.HTTPError):
    pass

class AdfException(Exception):
    pass
    
class eSCL():
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

    def is_escl_available(self, max_time = 60, loop_delay = 2):
        """
        Determines if eSCL is available. It will try for max_time seconds. It will return True if available
        and False if not

        Args:
            max_time (int): the number of seconds to wait for service to be available

            loop_delay (int): The number of seconds between loop

        Returns:
            bool: True if available otherwise False for not available
        
        """

        url_scanner_status = "http://{0}/eSCL/ScannerStatus".format(self.ip_address)
        log.debug(url_scanner_status)        
        is_escl_service_available = False
        start = time.time()
        log.debug("eSCL Waiting For Service Ready:  " + str(max_time) + " seconds")    
        while ((time.time() - start) < max_time):
            try:
                r = requests.get(url_scanner_status, verify=False, timeout=5)
                log.debug("r.status_code == {}".format(r.status_code))
                if r.status_code == 200:
                    is_escl_service_available =  True
                    break                 
            except requests.exceptions.ReadTimeout:
                pass
            time.sleep(int(loop_delay))
            log.debug("Waiting For Service Ready:" + str(int(time.time() - start)) + " of " + str(max_time))    
                
        return is_escl_service_available
        
    @property
    def is_adf_loaded(self):
        status = self.get_scanner_status()
        return "ScannerAdfLoaded".upper() in status.adf_state.upper()

    def get_scanner_status(self):
        """
        This will return the scanner status

        Args:

        Returns:
            ScannerStatus:  NamedTuple that will contain state and AdfState

        Raises:
            requests.exceptions.HTTPError: if status code is not 200

        """
        url_scanner_status = "http://{0}/eSCL/ScannerStatus".format(self.ip_address)
        log.debug(url_scanner_status)
        r = requests.get(url_scanner_status, verify=False, timeout=6)
        log.debug("r.status_code == {}".format(r.status_code))
        if r.status_code != 200:
            r.raise_for_status()
        log.debug("r.text == {}".format(r.text))
        state_re = re.compile('state')
        adf_state_re = re.compile('adfstate')
        soup = BeautifulSoup(r.text, 'html5lib')
        state = soup.find(state_re).text
        adfstate = soup.find(adf_state_re).text
        return ScannerStatus(state, adfstate)


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
        url_security_referer = "https://{}/hp/device/GeneralSecurity/Index".format(self.ip_address)
        
        with requests.Session() as s:
            r = s.get(url_security_referer, verify=False)
            if r.status_code != 200:
                raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_get_scan_config, r.status_code), response = r)
            soup = BeautifulSoup(r.text, 'html5lib')
            item = soup.find(lambda tag: tag.has_attr('id') and tag['id'] == "CSRFToken")
            if item is None:
                r = s.post(url_security_config, data = security_config_data, verify=False)
                if r.status_code != 200:
                    raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_security_config, r.status_code), response = r) 
            else:
                headers = {'Referer': url_security_referer}
                security_config_data["CSRFToken"] = item["value"]
                r = s.post(url_security_config, headers=headers, data = security_config_data, verify=False)
                if r.status_code != 200:
                    raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_security_config, r.status_code), response = r)
                time.sleep(1)
            
        with requests.Session() as s:
            r = s.get(url_get_scan_config, verify=False)
            if r.status_code != 200:
                raise  requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_get_scan_config, r.status_code), response = r)
            soup = BeautifulSoup(r.text, 'html5lib')
            item = soup.find(lambda tag: tag.has_attr('id') and tag['id'] == "IP_LAA")
            scan_config_data["IP_LAA"] = item["value"]
            item = soup.find(lambda tag: tag.has_attr('id') and tag['id'] == "CSRFToken")
            headers = {'Referer': url_security_referer}
            if item is not None:
                scan_config_data["CSRFToken"] = item["value"]        
            r = s.post(url_scan_config, data = scan_config_data, verify=False)
            if r.status_code != 200:
                raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_scan_config, r.status_code), response = r)    



    def scan_to_file(self, ticket, path_save_image_file,is_adf_loaded, number_of_images, image_name_suffix, wait_time_after_job_to_pull = 5):
        """
        It will create a scan job based on the ticket. It will save image to 
        path_save_image_file

        Args:

        ticket (str): The escl job ticket. 
        path_save_image_file (str): the path to save image file
        is_adf_loaded (bool) = determines if adf load should be loaded
        wait_time_after_job_to_pull: how long to wait to pull image after initiate scan image

        Raises:
            Exception: if ADF Target is not loaded
        """
        if is_adf_loaded:
            scanner_state = self.get_scanner_status()
            if "Loaded" not in scanner_state.adf_state:
                raise AdfException(scanner_state.adf_state)

        url_scan_job = "http://{0}/eSCL/ScanJobs".format(self.ip_address)
        log.debug(url_scan_job)
        response = requests.post(url_scan_job, data=ticket)
        if response.status_code != 201:
            if response.status_code == 409:
                raise InvalidTicketFormat("Invalid Scan Ticket option.", response = response)
            raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(url_scan_job, response.status_code))

        scan_image_url = response.headers["Location"] + "/NextDocument"
        log.debug(scan_image_url)
        time.sleep(wait_time_after_job_to_pull)
        loopcnt = 1
        image_file_name_list = os.path.basename(path_save_image_file).split(".")
        image_number = 1
        image_file_name = os.path.basename(path_save_image_file).split(".")[0]
        images = []
        while True:
            scanner_status = self.get_scanner_status()
            log.debug("state = {0} AdfState = {1}".format(scanner_status.state, scanner_status.adf_state))
            r = requests.get(scan_image_url, verify= False, stream = True)
            if r.status_code == 404:
                break
            if r.status_code == 503:
                time.sleep(wait_time_after_job_to_pull)
                log.debug("sleep and retry pulling scan")
                if loopcnt > 5:
                    raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(scan_image_url, r.status_code), response = r)
                    break
                loopcnt = loopcnt+1
                continue
            if r.status_code != 200:
                raise requests.HTTPError("{0} failed:\nExpected: 200\nReceived: {1}".format(scan_image_url, r.status_code), response = r)

            image_dir_name = os.path.dirname(path_save_image_file)
            new_image_file_name = "{}_{}-{}_{}".format(image_file_name,image_number,number_of_images,image_name_suffix)
            path_save_image_file = "{}{}{}".format(image_dir_name,"\\",new_image_file_name)
            if not os.path.exists(image_dir_name):
                os.makedirs(image_dir_name)
            with open(path_save_image_file,'wb') as f:
                shutil.copyfileobj(r.raw, f)
                images.append(new_image_file_name)
            image_number += image_number
        return images

class ScannerStatusTemp():
    def __init__():
        self.version = ""
        self.state = ""
        self.state_reasons = ""
        self.adf_state = ""
        self.jobs_info = []
 
class ColorModes(Enum):
    black_and_white = "BlackAndWhite1"
    grayscale8 = "Grayscale8"
    grayscale16 = "Grayscale16"
    rgb24 = "RGB24"
    rbg48 = "RGB48"

class ContentType(Enum):
    tiff = "image/tiff"
    jpeg = "image/jpeg"
    pdf = "application/pdf"
    raw = "application/octet-stream"
    xml = "text/xml"
    
class InputSource(Enum):
    platen = "Platen"
    Feeder = "Feeder"

class StateReasons(Enum):
    none  = 0
    cover_open = 1
    media_jam = 2
    multiple_feed_error = 3
    attention_required = 4
    internal_storage_full = 5
    lamp_error = 6
    power_down = 7

class JobStateReason(Enum):
    none = 0
    job_canceled_at_device = 1 
    job_canceled_by_user = 2
    job_completed_successfully = 3 
    job_completed_with_errors = 4
    job_completed_with_warnings = 5 
    job_scanning = 6
    job_scanning_and_transfering = 7 
    job_timed_uut = 8
    job_transfering = 9 
    queued_in_device = 10
    scanner_stopped = 11
    job_held_by_service = 12

class ScanTicket():
    def __init__(self):
        self._height = 3300
        self._width = 2550
        self._x_offset = 0
        self._y_offset = 0
        self._x_resolution = 300
        self._y_resolution = 300
        self._compression_factor = 0
        self._brightness = 3
        self._contrast = 3
        self._autocrop = "false"
        self._duplex = "false"
        self._document_format_ex = "image/jpeg"
        self._color_mode = "RGB24"
        self._input_source = "Platen"
        self._feed_direction = "ShortEdgeFeed"

    @property
    def autocrop(self):
        return self._autocrop == "true"

    @autocrop.setter
    def autocrop(self, value):
        if value not in ["true", "false"]:
            raise ValueError("autocrop must be only True or False received {}".format(value))
        self._autocrop = value

    @property
    def duplex(self):
        return self._duplex == "true"

    @duplex.setter
    def duplex(self, value):
        if value not in ["true", "false"]:
            raise ValueError("duplex must be only true or false received {}".format(value))
        self._duplex = value

    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        self._height = int(value)

    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        self._width = int(value)

    @property
    def x_offset(self):
        return self._x_offset
    
    @x_offset.setter
    def x_offset(self, value):
        self._x_offset = int(value)

    @property
    def y_offset(self):
        return self._y_offset
    
    @y_offset.setter
    def y_offset(self, value):
        self._y_offset = int(value)

    @property
    def x_resolution(self):
        return self._x_resolution
    
    @x_resolution.setter
    def x_resolution(self, value):
        self._x_resolution = int(value)
    
    @property
    def y_resolution(self):
        return self._y_resolution
    
    @y_resolution.setter
    def y_resolution(self, value):
        self._y_resolution = int(value)
    
    @property
    def compression_factor(self):
        return self._compression_factor
    
    @compression_factor.setter
    def compression_factor(self, value):
        self._compression_factor = int(value)

    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, value):
        self._brightness = int(value)

    @property
    def contrast(self):
        return self._contrast
    
    @contrast.setter
    def contrast(self, value):
        self._contrast = int(value)

    @property
    def document_format_ex(self):
        return self._document_format_ex
    
    @document_format_ex.setter
    def document_format_ex(self, value):
        self._document_format_ex = value 

    @property
    def color_mode(self):
        return self._color_mode

    @color_mode.setter
    def color_mode(self, value):
        self._color_mode = value

    @property
    def input_source(self):
        return self._input_source

    @input_source.setter
    def input_source(self,value):
        self._input_source = value

    @property
    def feed_direction(self):
        return self._feed_direction

    @feed_direction.setter
    def feed_direction(self,value):
        if value not in ["ShortEdgeFeed", "LongEdgeFeed"]:
            raise ValueError("feed_directions must be only ShortEdgeFeed or LongEdgeFeed received {}".format(value))
        self._feed_direction = value
        
    def to_xml(self):
        temp = SCANNER_TEMPLATE_TICKET
        temp = temp.replace("<Height></Height>","<Height>{}</Height>".format(self.height))
        temp = temp.replace("<Width></Width>","<Width>{}</Width>".format(self.width))
        temp = temp.replace("<XOffset></XOffset>","<XOffset>{}</XOffset>".format(self.x_offset))
        temp = temp.replace("<YOffset></YOffset>","<YOffset>{}</YOffset>".format(self.y_offset))
        temp = temp.replace("<XResolution></XResolution>","<XResolution>{}</XResolution>".format(self.x_resolution))
        temp = temp.replace("<YResolution></YResolution>","<YResolution>{}</YResolution>".format(self.y_resolution))
        temp = temp.replace("<CompressionFactor></CompressionFactor>","<CompressionFactor>{}</CompressionFactor>".format(self.compression_factor))
        temp = temp.replace("<Brightness></Brightness>","<Brightness>{}</Brightness>".format(self.brightness))
        temp = temp.replace("<Contrast></Contrast>","<Contrast>{}</Contrast>".format(self.contrast))
        temp = temp.replace("<AutoCrop></AutoCrop>","<AutoCrop>{}</AutoCrop>".format(str(self._autocrop)))
        temp = temp.replace("<Duplex></Duplex>","<Duplex>{}</Duplex>".format(str(self._duplex)))
        temp = temp.replace("<DocumentFormatExt></DocumentFormatExt>","<DocumentFormatExt>{}</DocumentFormatExt>".format(self.document_format_ex))
        temp = temp.replace("<ColorMode></ColorMode>","<ColorMode>{}</ColorMode>".format(self.color_mode))
        temp = temp.replace('<InputSource xmlns="http://www.pwg.org/schemas/2010/12/sm"></InputSource>','<InputSource xmlns="http://www.pwg.org/schemas/2010/12/sm">{}</InputSource>'.format(self.input_source))
        temp = temp.replace('<FeedDirection></FeedDirection>','<FeedDirection>{}</FeedDirection>'.format(self._feed_direction))
        log.debug(temp)
        return temp

    def __repr__(self):
        temp = "\nheight = {}\n".format(self.height)
        temp += "width = {}\n".format(self.width)
        temp += "x_offset = {}\n".format(self.x_offset)
        temp += "y_offset = {}\n".format(self.y_offset)
        temp += "x_resolution = {}\n".format(self.x_resolution)
        temp += "y_resolution = {}\n".format(self.y_resolution)
        temp += "compression_factor = {}\n".format(self.compression_factor)
        temp += "brightness = {}\n".format(self.brightness)
        temp += "contrast = {}\n".format(self.contrast)
        temp += "autocrop = {}\n".format(self.autocrop)
        temp += "duplex = {}\n".format(self.duplex)
        temp += "document_format_ex = {}\n".format(self.document_format_ex)
        temp += "color_mode = {}\n".format(self.color_mode)
        temp += "input_source = {}\n".format(self.input_source)
        temp += "FeedDirection = {}\n".format(self._feed_direction)
        
        return temp

def create_scan_ticket_from_dict(scan_settings = {}):
    '''
        This function creates the scan ticket from a dictionary of settings.
        Valid scan ticket settings are 

        autocrop = true or false default false
        duplex = true or false default false
        height = int(value) default 3300
        width = int(value) defaul 2550
        x_offset = int(value) default 0
        y_offset = int(value) default 0
        x_resolution = int(value) default 300
        y_resolution = int(value) default 300
        compression_factor = int(value) default 0
        brightness = int(value) default 3
        contrast = int(value) default 3
        document_format_ex = image/jpeg or application/pdf or image/tiff default image/jpeg
        color_mode = RGB24 or Grayscale8 or BlackAndWhite1 default RGB24
        input_source = Feeder or Platen default Platen
        feed_direction = ShortEdgeFeed or LongEdgeFeed default is ShortEdgeFeed
        
        Note: the following entry will defaults the width and height entries above
              do not specify both height or width and PAPERSIZE or unpredictable results can happen.
        PAPERSIZE = A4 or A3 or LETTER or LEDGER
        
        example:
        xml_scan_ticket = create_scan_ticket_from_dict(settings_dict)
    '''
   
    MEDIA_SIZE_HEIGHT_LETTER_300 = 3300
    MEDIA_SIZE_WIDTH_LETTER_300 = 2550
    MEDIA_SIZE_HEIGHT_LEDGER_300 = 5100
    MEDIA_SIZE_WIDTH_LEDGER_300 = 3300
    MEDIA_SIZE_HEIGHT_A4_300 = 3508
    MEDIA_SIZE_WIDTH_A4_300 = 2480
    MEDIA_SIZE_HEIGHT_A3_300 = 4961
    MEDIA_SIZE_WIDTH_A3_300 = 3508
    
    if type(scan_settings) != dict:
        raise Exception("Syntax Error! Pass parameter must be a dictionary.")

    ticket = ScanTicket()
    
    for name,value in scan_settings.items():
        if hasattr(ticket,name):
            setattr(ticket,name,value)
            continue
        if name.upper() == "PAPERSIZE":
            #print(name.upper(),value.upper())
            if value.upper() == "A4":
                ticket.height =  MEDIA_SIZE_HEIGHT_A4_300
                ticket.width = MEDIA_SIZE_WIDTH_A4_300
            if value.upper() == "A3":
                ticket.height =  MEDIA_SIZE_HEIGHT_A3_300
                ticket.width = MEDIA_SIZE_WIDTH_A3_300       
            if value.upper() == "LETTER":
                ticket.height =  MEDIA_SIZE_HEIGHT_LETTER_300
                ticket.width = MEDIA_SIZE_WIDTH_LETTER_300
            if value.upper() in ["LEDGER","LGR"]:
                ticket.height =  MEDIA_SIZE_HEIGHT_LEDGER_300
                ticket.width = MEDIA_SIZE_WIDTH_LEDGER_300
            continue
        raise InvalidTicketFormat("ScanTicket Property '{0}' does not exist.".format(name))

    return ticket.to_xml()
