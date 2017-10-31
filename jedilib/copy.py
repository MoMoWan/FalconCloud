"""
    Copy Pillar
    Creates a copy object and you can set properties of the object
    
"""
__version__ = "$Revision: 47957 $"
__author__  = "$Author: dfernandez $"
__date__    = "$Date: 2016-05-27 14:37:21 -0600 (Fri, 27 May 2016) $ "
 
 # =============================================================================
# Standard Python modules
# =============================================================================
import os
import sys
import time


# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger("jedilib")

# =============================================================================
# .NET modules
# =============================================================================

import clr
jedi_dll = os.path.join(os.path.dirname(__file__), "HP.Falcon.JediNG.dll")
clr.AddReference(jedi_dll)
from HP.Falcon.JediNG.WebServices.Copy import CopyClient
from HP.Falcon.JediNG.WebServices.Common import FalconXElement

# =============================================================================
# Globals and Definitions
# =============================================================================

class Copy():
    def __init__(self, ip_address):
        self._ip_address = ip_address
                                
        
    
    def get_copy_sides_default(self):
        '''
        SCIP possible values are integrationSetupInProgress, noIntegrationInProgress,
        notSupported, readyForIntegration, readyToShip
        '''
        client = CopyClient(self._ip_address)
        ticket = client.GetTicket()
        t = FalconXElement(ticket)
        result = t.GetValue("CopySides")
        return result

        
    
    def put_copy_sides_default(self, value):
        '''
        SCIP possible values are "simplexToSimplex", "simplexToDuplex", "duplexToSimplex",
        "duplexToDuplex"
        '''
            
        valid_value = ("simplexToSimplex", "simplexToDuplex", "duplexToSimplex", "duplexToDuplex")
        if value not in valid_value:
           ValueError("{} invalid input. Valid inputs are {}".format(value, valid_value))

        ticket = self.get_copy_default_job()
        result = FalconXElement(ticket)
        result.FindElement("CopySides").SetValue(value)
        self.put_copy_default_ticket(result.ToXElement())

    def get_copy_default_job(self):
        client = CopyClient(self._ip_address)
        ticket = client.GetDefaultJob()
        return ticket
        

    def get_copy_default_ticket(self):        
        t = FalconXElement(self.get_copy_default_job())
        return t.ToString()

    def put_copy_default_ticket(self, ticket):
        client = CopyClient(self._ip_address)
        client.PutDefaultJob(ticket)
         