"""
manufacturing_proxy.py
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
from collections import defaultdict
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
from HP.Falcon.JediNG.WebServices.Manufacturing import ManufacturingServiceClient
from HP.Falcon.JediNG.WebServices.Common import  FalconXElement
# =============================================================================
# Globals and Definitions
# =============================================================================

class PrintInternalPageGuids():
    ColorBandTest = "3e8980ac-3b1c-409e-9df5-4ec026069e3d"
    ColorUsageJobLog = "37e25f7d-7642-452f-926a-d1cafa8e0772"
    ConfigurationPage = "b64e0a99-e520-4ab6-abf3-40ca120065d9"
    DiagnosticsPage = "dcbc9605-8872-4947-ad92-10d2af721027"
    FileDirectoryPage = "5500e5fd-d71c-44f1-97c6-bdbfe224c473"
    HowToConnectPage = "b6770c73-ab05-4882-9a42-36178f288af8"
    PrintQualityPages = "6ce6dd73-2a0e-47d4-a582-24e9657f76ef"
    PrintQualityPages2 = "bc23237a-1522-48a1-b876-7366aa87e82b"
    FuserTestPage = "3051bcd8-2b3c-46f0-b39a-5acf282bd60b"
    SettingsMenuMap = "5fe408cb-c6d6-4632-ba88-e06bcade41a1"
    SuppliesStatusPage = "b9c7a9b9-b50c-4c5c-bdeb-925d993b437d"
    UsagePage = "2c9e8352-7c60-4dfc-aba1-20baeb5e8448"
    WebServicesStatusPage = "e7180330-5037-4c9c-9cd0-38f7f82dd25d"
    Tap10 = "cd21820e-4dfc-4e27-9d23-77196e5d0621"
    Tap11 = "7018c29c-a2c2-4327-b907-1241da02818f"
    Tap12 = "3d4c7d08-b8b1-4679-9c1f-424b3cea0d5e"
    Tap15 = "2f031786-fafa-4d44-8921-782762148143"
    Tap17 = "950c3832-262b-4916-9e83-e08b4ccf0e5c"
    Tap43 = "a83b1678-d3ca-4847-a1e6-1df2167e4332"
    Tap60 = "832a5914-9ddc-48fb-a3a1-993b7901f2e4"
    Tap61 = "1eeaaf83-9294-4351-ad87-ff3dd11a2a06"
    Tap63 = "a0c0857a-69b2-41ff-8ce7-8ec52c81d4e1"
    Tap65 = "e4039ffc-31a9-4089-b274-cb31f710c0fe"
    Tap262 = "817dc80a-dede-44a1-8cd0-f8959ddf40b2"
    Tap909 = "7c524791-52d6-40bc-a47b-aa11493a94bf"



class Manufacturing(object):
    def __init__(self, ip_address):
        self._ip_address = ip_address
        
    
    def PrintInternalPage(self, guid):
        '''
        Print Internal Page based on guid. It returns True or False if it succeeds
        '''
        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = client.PrintInternalPage(guid)
            client.Close()
            return result
        except:
            client.Abort
            raise
            
        
    def IsWebServiceReady(self, total_time, sleep_time=0.5):
        '''
        Wait for time seconds for Web Service is ready
        '''
        start_time = time.time()
        elapsed_time = time.time() - start_time
        while elapsed_time < total_time:
            try:
                data = self.GetXmlTicket()
                if data is not None:
                    return True
            except:
                time.sleep(sleep_time)
                elapsed_time = time.time() - start_time
        return False

    @property
    def EnginePassThroughMode(self):
        """
        returns the EnginePassThroughMode value enabled/disabled
        """
        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = FalconXElement(client.GetServiceDeviceConfiguration())
            client.Close()
            return result.GetValue("EnginePassThroughMode")
        except:
            client.Abort()
            raise
    
    @EnginePassThroughMode.setter
    def EnginePassThroughMode(self, value):
        if value not in ("enabled", "disabled"):
            raise Exception("can only be set to enabled or disabled")

        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = FalconXElement(client.GetServiceDeviceConfiguration())
            result.FindElement("EnginePassThroughMode").SetValue(value)
            client.PutServiceDeviceConfiguration(result.ToXElement())
            client.Close()
        except:
            client.Abort()
            raise

    def GetXmlTicket(self):
        """
        returns the EnginePassThroughMode value enabled/disabled
        """
        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = client.GetXmlTicket()
            client.Close()
            return result
        except:
            client.Abort
            raise
        
    def SendEngineCommand(self, command):
        '''
        Send engine command
        '''

        if command.startswith("SR"):
            cc = int(command[2:])<<1
            if str(cc).count("1")%2 == 1:
                cc = cc+1
            log.debug(str.format("SR command {0} converted to {1:0>4x} command code",command,cc))
            command = str.format("{0:0>4x}",cc)
        c = command
        if type(command) is str:
            c = int(command,16)
        client = ManufacturingServiceClient(self._ip_address)                    
        
        engCmdReq = command
        if type(command) is str:
            engCmdReq = int(command,16)
            
        log.debug(str.format("Sending engine Command {0:0>4x}",c))
        result = client.SendEngineCommand(engCmdReq)
        log.debug(str.format("{0:0>4x}", int(result)))
        client.Close()
        return int(result)

        
    @property
    def EngineStatuses(self):
        '''
        s = ticket.FindElements("EngineStatuses")
        for i in s:
            print(i)
        mfg_data = self._mfg_web_service.GetSettings()
        return list(mfg_data.EngineStatuses)
        '''
    
    @property
    def EngineStatusesHR(self):
        srList = defaultdict(lambda: "0000")
        for stat in self.EngineStatuses:
            keyName = "SR" + str(int(stat.Code) >> 1).upper()
            log.debug(str.format("stat.Code {0} | stat.CurrentStats: {1}",stat.Code,stat.CurrentStatus))
            srList[keyName] = str.format("{0:0<4x}", int(stat.CurrentStatus)).upper()
        
        return srList
        
    @property
    def EngineStatusesValue(self):
        srList = defaultdict(lambda: 0)
        for stat in self.EngineStatuses:
            keyName = "SR" + str(int(stat.Code) >> 1).upper()
            srList[keyName] = int(stat.CurrentStatus)
        
        return srList
        
        
    @property
    def SCIP(self):
        '''
        SCIP possible values are integrationSetupInProgress, noIntegrationInProgress, notSupported, readyForIntegration, readyToShip
        '''
        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = client.GetSCIP()
            client.Close()
            return result
        except:
            client.Abort()
            raise
        
    @SCIP.setter
    def SCIP(self, value):
        client = ManufacturingServiceClient(self._ip_address)
        try:
            result = FalconXElement(client.GetServiceDeviceConfiguration())
            result.FindElement("SCIP").SetValue(value)
            client.PutServiceDeviceConfiguration(result.ToXElement())
            client.Close()
        except:
            client.Abort
            raise