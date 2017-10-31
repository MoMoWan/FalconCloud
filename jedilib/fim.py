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

class Fim():
    def __init__(self, ip_address):
        self._ip_address = ip_address
                                
    def is_available(self, wait_time = 60, time_delay = 0.5):
        """
        determine if FIM web service is available

        Args:
            wait_time (int): The amount of time to wait
            time_delay (int): The amount of time to wait between loops

        Returns:
            bool: True if available else False if not available
                
        """
        start = time.time()
        log.info("Waiting For FIM  for " + str(wait_time))  
        while ((time.time() - start) < int(wait_time)):
            try:
                client = WSTransferClient(self._ip_address, "fim")
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
        
    def download(self, file_path, user_name="admin", password=""):
        """
        Download FIM Bundle to printer via FIM Web Service

        Args:
            file_path (str): full path to the fim bundle
        """
        fim_client = FimProxy(self._ip_address)
        fim_client.SendTimeout = "600"
        fim_client.RecieveTimeout = "600"
        fim_client.Download(file_path, user_name, password)

    def get_fim_service_ticket(self):
        """
        Get FIM Service Ticket resource urn:hp:imaging:con:service:fim:FIMService

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        return self.get_fim_resource("urn:hp:imaging:con:service:fim:FIMService")

    def get_fim_service_default_ticket(self):
        """
        Get FIM Service Default Ticket resource urn:hp:imaging:con:service:fim:FIMService:ServiceDefaults

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        return self.get_fim_resource("urn:hp:imaging:con:service:fim:FIMService:ServiceDefaults")
        
    def get_fim_service_assets_ticket(self):
        """
        Get FIM Service Assets Ticket resource urn:hp:imaging:con:service:fim:FIMService:Assets

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        return self.get_fim_resource("urn:hp:imaging:con:service:fim:FIMService:Assets")

    def get_fim_resource(self, resource):
        """
        Get FIM Service Resource Ticket 

        Args:
            resource (str): urn for the resource like 
                resource urn:hp:imaging:con:service:fim:FIMService:Assets

        Returns:
            FalconXElement: XElement data that contains fim service data
                
        """
        client = WSTransferClient(self._ip_address, "fim")
        try:
            log.debug("resource = {}".format(resource))
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
            
        
         