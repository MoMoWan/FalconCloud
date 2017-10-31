"""
print_calibration.py
"""
__version__ = "$Revision: 47957 $"
__author__  = "$Author: dfernandez $"
__date__    = "$Date: 2016-05-27 14:37:21 -0600 (Fri, 27 May 2016) $ "
 

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
from collections import defaultdict
from enum import IntEnum
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
from HP.Falcon.JediNG.WebServices.PrintCalibration import PrintCalibrationServiceClient
from HP.Falcon.JediNG.WebServices.Common import  FalconXElement
# =============================================================================
# Globals and Definitions
# =============================================================================

class RemotePrintCalibrationType(IntEnum):
    ColorPlaneRegistration = 0
    ConsecutiveDmaxDhalf = 1
    ErrorDiffusion = 2
    DrumSpeedAdjustment = 3
    PulseWidthModulation = 4
    Test = 5
    AlternateDhalf = 6
    ConsecutiveCPRDmaxDhalf = 7
    DensityUniformityAdjustment = 8
    OnPaperCalibrationLetter = 9
    OnPaperCalibrationA4 = 10
    OnPaperCalibrationLedger = 11
    OnPaperCalibrationA3 = 12
    OrderedDitherDensityMeasurement = 13
    PenAlignmentChain = 14
    ColorCalChain = 15
    DropDetect = 16
    Zim = 17
    BDDBeamCenter = 18
    KDropDetect = 19
    PenHeight = 20
    OOBEChain = 21
    KCMYDropDetect = 22
    PQChain = 23
    PenAlign1 = 24
    PenAlign2 = 25
    PenAlign3 = 26
    CCFirstPageWTTOE = 27 
    CCSecondPage = 28
    CCThirdPage = 29
    CCFirstPageWoTTOE = 30
    BlackStrip = 31
    ZimOnlyPrinting = 32
    CleanPrintheadDropDetect = 33
    CCPrewarm1 = 34
    CCPrewarm2 = 35
    PenServiceLevel1 = 36
    PenServiceLevel2 = 37
    PenServiceLevel3 = 38
    PenRecoveryLevel1 = 39
    MechServiceCleanInkSmear = 40
    MechServiceCleanInkShim = 41
    MechServiceMaintenance = 42
    MechBeamCenter = 43
    MechPenHeight = 44
    ScanBarScan = 45
    LLVStep1 = 46
    LLVStep2 = 47
    LVStep3 = 48


class PrintCalibration(object):
    def __init__(self, pc_address, ip_address):
        self._pc_address = pc_address
        self._ip_address = ip_address
        
    
    def RequestCalibration(self, calibration_type):
        '''
        Print Internal Page based on guid. It returns True or False if it succeeds
        '''
        client = PrintCalibrationServiceClient(self._pc_address, self._ip_address)
        try:
            calibration_type = RemotePrintCalibrationType(calibration_type)
            result = client.RequestCalibration(calibration_type)
            return result
        except Exception as e:
            log.debug("error in PrintCalibrationServiceClient trying to calibrate: " + str(e))
            raise Exception(e)
            
    def RequestCalibrationAndWait(self, calibration_type, time_out):
        '''
        Print Internal Page based on guid. It returns True or False if it succeeds
        '''
        client = PrintCalibrationServiceClient(self._pc_address, self._ip_address)
        try:
            calibration_type = RemotePrintCalibrationType(calibration_type)
            result = client.RequestCalibration(calibration_type, time_out)
            return result
        except Exception as e:
            log.debug("error in PrintCalibrationServiceClient trying to calibrate: " + str(e))
            raise Exception(e)
            
        
    def IsWebServiceReady(self, total_time, sleep_time=0.5):
        '''
        Wait for time seconds for Web Service is ready
        '''
        start_time = time.time()
        elapsed_time = time.time() - start_time
        while elapsed_time < total_time:
            try:
                self.GetXmlTicket()
                return True
            except:
                time.sleep(sleep_time)
                elapsed_time = time.time() - start_time
        return False

    def GetXmlTicket(self):
        """
        returns the EnginePassThroughMode value enabled/disabled
        """
        client = PrintCalibrationServiceClient(self._pc_address, self._ip_address)
        try:
            result = client.GetPrintCalibrationServiceTicket()
            return result
        except:
            print("Failed to get Service Ticket XML")
    
    def GetXmlTicketAsDataList(self):
        """
        Returns the XML Ticket after Calibration in a dataList
        """
        client = PrintCalibrationServiceClient(self._pc_address, self._ip_address)
        try:
            result = client.GetPrintCalibrationServiceTicket()
            data = self.ParseXmlTicket(result)
            return data
        except:
            print("Failed to get Service Ticket Data")
            
    def GetLastCalibrationExecutionData(self):
        '''
        Send engine command
        '''
        client = PrintCalibrationServiceClient(self._pc_address, self._ip_address)
        try:
            result = client.GetLastCalibrationExecutionData()
            return result
        except:
            return False
            
    def ParseXmlTicket(self, xml_return_data):
        """
        Parse response XML Ticket data and returns a list of values
        """
        xml_string = xml_return_data.ToString()
        value_start = "<printcalibration:Value>"
        yellow_start = "<printcalibration:YellowData>"
        black_end = "</printcalibration:BlackData>"
        
        index_start = xml_string.index(yellow_start)
        index_end = xml_string.index(black_end)
        data = []
        value = ''
        while index_start < index_end:
            try:
                index_start = index_start + xml_string[index_start:].index(value_start) + len(value_start)
            except ValueError:
                break
            while xml_string[index_start:index_start+1] != '<' and index_start < index_end:
                value = value + xml_string[index_start:index_start+1]
                index_start = index_start + 1
            data.append(value)
            value = '' 
        return data
        
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