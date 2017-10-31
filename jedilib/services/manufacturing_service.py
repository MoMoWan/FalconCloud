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
# Python Libraries
# =============================================================================

from .soap import WSTransferSoapMessage
from .soap.client import SoapClient
from .soap import SoapFaultException


# =============================================================================
# Globals and Definitions
# =============================================================================

class ManufacturingService():
    def __init__(self, ip_address,is_secure=True):
        self.is_secure = is_secure
        self.ip_address = ip_address
        self.service = "manufacturing"
        self.port = 56728
        if self.is_secure:
            self.port = 7627

    
        self.manufacturing_service = "urn:hp:imaging:con:service:manufacturing:ManufacturingService"
        self.manufacturing_service_prompts = "urn:hp:imaging:con:service:manufacturing:ManufacturingService:Prompts"
        self.manufacturing_service_device_configuration = "urn:hp:imaging:con:service:manufacturing:ManufacturingService:DeviceConfiguration"
        self.soap_client = SoapClient(self.ip_address,port=self.port,service=self.service,is_secure=self.is_secure)
        
                                
    def is_available(self, wait_time = 60, time_delay = 0.5):
        """
        determine if Manufacturing web service is available

        Args:
            wait_time (int): The amount of time to wait
            time_delay (int): The amount of time to wait between loops

        Returns:
            bool: True if available else False if not available
                
        """
        start = time.time()
        log.info("Waiting For Manufacturing  for " + str(wait_time)) 
        while ((time.time() - start) < int(wait_time)):
            try:
                self._get_resource(self.manufacturing_service)
                return True
            except Exception as ex:
                log.debug("ServiceModel.EndpointNotFoundException at ip {}".format(self._ip_address))
                curTime = int(time.time() - start)
                log.info("Waiting For Ris : {} of {}".format(curTime,wait_time)) 
                time.sleep(int(time_delay))
                continue
                
        return False
    
    def get_service_ticket(self):
        """
        Get Manufacturing Service Ticket resource urn:hp:imaging:con:service:manufacturing:ManufacturingService

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        return self._get_resource("urn:hp:imaging:con:service:manufacturing:ManufacturingService")

    def _get_resource(self, resource):
        """
        Get FIM Service Resource Ticket 

        Args:
            resource (str): urn for the resource like 
                resource urn:hp:imaging:con:service:fim:FIMService:Assets

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """

        msg = WSTransferSoapMessage(
            action="Get", 
            service=self.service,
            resource=resource,
            data="",
            ip_endpoint=self.ip_address,
            is_secure=self.is_secure).tostring() 
        
        ticket =  self.soap_client(msg)
        return ticket
        