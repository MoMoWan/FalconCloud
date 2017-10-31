"""
    Jedi FIM Web Service
    
"""
__version__ = "$Revision: 47957 $"
__author__  = "$Author: dfernandez $"
__date__    = "$Date: 2016-05-27 14:37:21 -0600 (Fri, 27 May 2016) $ "
 

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import time


# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# .NET modules
# =============================================================================

import clr
jedi_dll = os.path.join(os.path.dirname(__file__), "HP.Falcon.JediNG.dll")
clr.AddReference(jedi_dll)
from HP.Falcon.JediNG.WebServices.WSTransfer import WSTransferClient
from HP.Falcon.JediNG.WebServices.Fim import FimClient, FimProxy
from HP.Falcon.JediNG.WebServices.Common import  FalconXElement
from System import ServiceModel, TimeoutException

# =============================================================================
# Globals and Definitions
# =============================================================================

class FaxService():
    def __init__(self, ip_address):
        """
        This will construct the Security Service with initial ip address

        Args:
            ip_address (str): The IP address of device
        """
        self._ip_address = ip_address
        self._service = "fax"
                                
    def is_available(self, wait_time = 60, time_delay = 0.5):
        """
        determine if web service is available

        Args:
            wait_time (int): The amount of time to wait
            time_delay (int): The amount of time to wait between loops

        Returns:
            bool: True if available else False if not available
                
        """
        start = time.time()
        log.info("Waiting For {}  for {} seconds".format(self._service, wait_time))
        wait_time = int(wait_time)  
        while ((time.time() - start) < wait_time ):
            try:
                client = WSTransferClient(self._ip_address, self._service)
                client.Operationimeout = 2
                resource = "urn:hp:imaging:con:service:fax:FaxService"
                ticket = client.Get(resource)
                client.Close()
                return True
            except ServiceModel.EndpointNotFoundException as ex:
                log.debug("ServiceModel.EndpointNotFoundException at ip {}".format(self._ip_address))
                client.Abort()
                curTime = int(time.time() - start)
                log.info("Waiting For Ris : {} of {}".format(curTime,wait_time)) 
                time.sleep(int(time_delay))
                continue
            except TimeoutException as ex:
                log.debug("TimeoutException at ip {}".format(self._ip_address))
                client.Abort()
                curTime = int(time.time() - start)
                log.info("Waiting For Ris : {} of {}".format(curTime,wait_time)) 
                time.sleep(int(time_delay))
                continue
                
        return False
        
    def set_analog_fax_default_tray(self, country="unitedStates", company_name="HP-MFG", fax_num="102", tray="Tray2", service_enabled = "enabled"):
        """
        Set the Analog fax Settings
        country (str): The country name like unitedStates
        company_name (str): the company like HP-MFG
        fax_num (str): fax number like 102
        tray (str): tray number like Tray2
        service_enabled (str): enabled or disabled service 
        """
        t = self.get_fax_service_ticket()
        t.FindElement("AnalogFaxCountry").SetValue(country)
        t.FindElement("CompanyName").SetValue(company_name)
        t.FindElement("FaxNumber").SetValue(fax_num)
        t.FindElement("DefaultFaxInputTray").SetValue(tray)
        t.FindElement("FaxMethod").SetValue("internalModem")
        self.put_resource("urn:hp:imaging:con:service:fax:FaxService", t)
        t = self.get_resource("urn:hp:imaging:con:service:fax:FaxService:ServiceDefaults")
        for f in t.FindElements("FaxServiceEnabled"):
            f.SetValue(service_enabled)
        self.put_resource("urn:hp:imaging:con:service:fax:FaxService:ServiceDefaults", t)

    def get_fax_service_ticket(self):
        """
        Get Fax Service Ticket

        Returns:
            FalconXElement: The XElement ticket
        """
        return self.get_resource("urn:hp:imaging:con:service:fax:FaxService")

    def get_resource(self, resource):
        """
        Get Service Resource Ticket 

        Args:
            resource (str): urn for the resource like 
                resource urn:hp:imaging:con:service:fim:FIMService:Assets

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        client = WSTransferClient(self._ip_address, self._service)
        try:
            log.debug("get resource = {} for sevice endpoint = {}".format(resource, self._service))
            ticket = client.Get(resource)
            client.Close()
            return FalconXElement(ticket)
        except ServiceModel.EndpointNotFoundException as ex:
            log.debug("ServiceModel.EndpointNotFoundException at ip {}".format(self._ip_address))
            client.Abort()
            raise
        except TimeoutException as ex:
            log.debug("TimeoutException at ip {}".format(self._ip_address))
            client.Abort()
            raise
            
    def put_resource(self, resource, ticket):
        """
        """

        client = WSTransferClient(self._ip_address, self._service)
        try:
            log.debug("put resource = {} for sevice endpoint = {}".format(resource, self._service))
            client.Put(resource, ticket)
            client.Close()
        except ServiceModel.EndpointNotFoundException as ex:
            log.debug("ServiceModel.EndpointNotFoundException at ip {}".format(self._ip_address))
            client.Abort()
            raise
        except TimeoutException as ex:
            log.debug("TimeoutException at ip {}".format(self._ip_address))
            client.Abort()
            raise

         
