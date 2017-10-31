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

class SecurityService():
    def __init__(self, ip_address):
        """
        This will construct the Security Service with initial ip address

        Args:
            ip_address (str): The IP address of device
        """
        self._ip_address = ip_address
        self._service = "security"
                                
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
                resource = "urn:hp:imaging:con:service:fim:FIMService"
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
        
    
    def set_security_service_element(self, element, value):
        """
        """
        ticket = self.get_security_service_ticket()
        ticket.FindElement(element).SetValue(value)
        self.put_resource("urn:hp:imaging:con:service:security:SecurityService", ticket)
        
    def set_security_service_elements(self, elements):
        """
        """
        ticket = self.get_security_service_ticket()
        for element, value in elements.items():
            ticket.FindElement(element).SetValue(value)

        self.put_resource("urn:hp:imaging:con:service:security:SecurityService", ticket)

    def get_security_service_ticket(self):
        """
        Get Security Service Ticket

        Returns:
            FalconXElement: The XElement ticket
        """
        return self.get_resource("urn:hp:imaging:con:service:security:SecurityService")

    def get_wireless_direct_print_setting(self):
        """
        This will return the WirelessDirectPrint Setting  
        Args:d
            
        Returns:
            str: enabled/disabled
        """

        ticket = self.get_security_service_ticket()
        return ticket.FindElement("WirelessDirectPrint").Value

    def set_wireless_direct_print_setting(self, state):
        """
        This will enable/disable WirelessDirectPrint Setting  
        Args:
            state (bool): True - enable False - disable
        """

        value = "enabled"
        if not state:
            value = "disabled"

        self.set_security_service_element("WirelessDirectPrint", value)

    def get_nfc_state_setting(self):
        """
        This will return the NFC State Setting  
        Args:
            
        Returns:
            str: enabled/disabled
        """

        ticket = self.get_security_service_ticket()
        return ticket.FindElement("State").Value

    def set_nfc_state_setting(self, state):
        """
        This will enable/disable NFC 
        Args:
            state (bool): True - enable False - disable
        """

        value = "enabled"
        if not state:
            value = "disabled"

        self.set_security_service_element("State", value)

    
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

         