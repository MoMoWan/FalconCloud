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
import time
import binascii

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
from HP.Falcon.JediNG.WebServices.Qualification.RemoteInvocation import RemoteInvocationClient

# =============================================================================
# Globals and Definitions
# =============================================================================


# =============================================================================
# Falcon Python modules
# =============================================================================
class RemoteTask(object):
    def __init__(self, ip_address):
        self.ip_address = ip_address
        
        
    def RunTask(self, taskName, methodIdentifier, parameters = None):
        """
        Tells the RemoteInvocationService to execute an IQualificationTask that is in Jedi.
      
        Args:
        taskName (str) - the name of the IQualificationTask running on the device
        methodIdentifier (str) - if the task has multiple subtasks each subtask will be identified by the optional methodIdentifier
        parameters (list)- list of any optional string parameters that the task expects
        
        Returns:
            (str)- string response from the IQualificationTask
        """
        from System import Array
        p = None
        if parameters != None:
            p = Array[str](parameters)
        log.debug(str.format("RunTask({0}, {1}, {2})", taskName, methodIdentifier, p))
        client = RemoteInvocationClient(self.ip_address)
        try:
            v = client.RunTask(taskName, methodIdentifier, p)
            client.Close()
            return v
        except:
            client.Abort()
            raise
        
        
    def ClearAllData(self):
        """
        Clears Customer, Machine, and extensibility data on the device
        """
        args = None
        self.RunTask("RisDeviceTask", "clearalldata", args)
        
    def ClearCustomerData(self):
        """
        Clears Customer data on the device
        """
        args = None
        self.RunTask("RisDeviceTask", "clearcustomerdata", args)
        
    def CreateFileOnReadOnlyPartition(self, fileName, partition, text):
        """
        creates a file on a read only partition
        fileName - The file to create on the partition
        partition - the partition to create the file on, like PREBOOT
        text - the text to write to the file after creating it
        """
        args = [fileName, partition, text]
        self.RunTask("StorageManagerTask", "CreateFileOnReadOnlyPartition", args)

    def delete_spi_save_recover_guid_id_nvp(self, guid = "D2B9F4DC-B3BD-47a9-8444-46B6D8338778"):
        """
        Delete SPI Save Recover ID ManufSRClientSpiStorageId
        D2B9F4DC-B3BD-47a9-8444-46B6D8338778,ManufSRClientSpiStorageId

        Args:
            guid (str): GUID for SPI Save Recover ID
        """
        self.DeletetAllSpiNVPsForGuid("D2B9F4DC-B3BD-47a9-8444-46B6D8338778")

    def DeleteFileOnReadOnlyPartition(self, fileName, partition):
        """
        Deletes a file on a read-only partition
        fileName - The file to delete on the partition
        partition - The partition to delete the file, like PREBOOT
        """
        args = [fileName, partition]
        self.RunTask("StorageManagerTask", "DeleteFileOnReadOnlyPartition", args)
        
    def BreadCrumb(self):
        """
        return UI BreadCrumb 
        """
        return self.RunTask("RisDeviceTask","breadcrumb", None)
        
    def ClearAllData(self):
        return self.RunTask("RisDeviceTask","clearalldata", None)

    def ClearRingBuffer(self):
        """
        It will clear out the ring buffer
        """
        self.RunTask('ComponentManagerTask','ClearAllRingBuffers', None) 
        
    def ControlPanelStatus(self):
        return self.RunTask("RisDeviceTask","controlpanelstatus", None)
    
    def get_secure_disk_status(self, guid = "E8D56211-1010-4A25-B6AB-D1AB7E98A217"):
        """
        Gets the NVP SecureDiskStatus Status

        Args:
            guid (str): The guid of SecureDiskStatus

        Returns:
            str : The hex string value of SecureDiskStatus
        """
        return self.GetSpiNvpValue(guid,"SecureDiskStatus")

    def get_falcon_jedi_state(self, guid="D7BFA98C-6389-4661-8ED2-FC3775A800E0"):
        """
        Gets the falcon jedi state

        Args:
            guid (str): The guid for FalconJediState NVP

        Returns:
            str : The string value of FalconJediState
        """

        return self.GetSpiNvpValue(guid, "FalconJediState")

    def get_execution_mode(self, guid="0429E79E-D9BA-412E-A2BC-1F3d245041CE"):
        """
        Gets the falcon jedi state

        Args:
            guid (str): The guid for ExecutionMode NVP

        Returns:
            str : The string value of ExecutionMode
        """

        return self.GetSpiNvpValue(guid, "ExecutionMode")

    def GetInactivityTimeout(self):
        return self.RunTask("HP.Mfp.App.ControlPanel.Framework.ControlPanelUtilitiesTask","GetInactivityTimeout", None)
        
    def GetLedReady(self):
        """
        Get the State of the Ready LED it is either on or off
        """
        return self.RunTask("LedProviderTask", "ReadyLed", None)
        
    def GetLedData(self):
        """
        Get the State of the Data LED it is either on or off
        """
        return self.RunTask("LedProviderTask", "DataLed", None)
        
    def GetLedAttention(self):
        """
        Get the State of the Attention LED it is either on or off
        """
        return self.RunTask("LedProviderTask", "AttentionLed", None)

    def get_ring_buffers(self):
        """
        returns the string contents of the ring buffer
        """
        return self.RunTask('ComponentManagerTask','DumpAllRingBuffers', None) 
        
    def IsAvailable(self, time_to_wait, timeToDelay = 1):
        """
        It checks if RIS is available within time_to_wait seconds
        """
        start = time.time()
        log.info("Waiting For RIS  for " + str(time_to_wait))  
        while ((time.time() - start) < int(time_to_wait)):
            try:
                client = RemoteInvocationClient(self.ip_address)
                client.Operationimeout = 2
                client.RunTask("RisDeviceTask", "geterrorlogentries", None)
                client.Close()
                return True
            except:
                log.exception("Error occurred")
                client.Abort()
                curTime = int(time.time() - start)
                log.info("Waiting For Ris : " + str(curTime) + " of " + str(time_to_wait)) 
                time.sleep(int(timeToDelay))
                continue
                
        return False
        
    def SetInactivityTimeout(self, value):
        v = [str(value)]
        return self.RunTask("HP.Mfp.App.ControlPanel.Framework.ControlPanelUtilitiesTask","SetInactivityTimeout", v)

    def set_falcon_jedi_state(self, value, guid="D7BFA98C-6389-4661-8ED2-FC3775A800E0"):
        """
        Gets the falcon jedi state

        Args:
            value (str): The value to set Falcon Jedi State
            guid (str): The guid for FalconJediState NVP

        """
        v = binascii.hexlify(value.encode()).decode()
        log.debug("Set Value {} Hex Value {} ".format(value, v))
        self.SetSpiNvpValue(guid,"FalconJediState", v)
    
    def GetEventLogEntryCount(self):
        """
        Get event log entry count for error, warning, and info
        """
        class EventLogEntryCount(object):
            def __init__(self, errorCount, warningCount, infoCount):
                self.ErrorCount = errorCount
                self.WarningCount = warningCount
                self.InfoCount = infoCount
                
        errorCount = self.RunTask('RisDeviceTask', 'GetEventLogEntryCount', ["error"])
        warningCount = self.RunTask('RisDeviceTask', 'GetEventLogEntryCount', ["warning"])
        infoCount = self.RunTask('RisDeviceTask', 'GetEventLogEntryCount', ["info"])
        return EventLogEntryCount(errorCount, warningCount, infoCount)

    def GetErrorLogEntries(self):
        return self.RunTask("RisDeviceTask", "geterrorlogentries", None)
        
    def Reboot(self):
        self.RunTask("HP.Common.Services.StateSchedulerTask", "requestreboot", None)
        
    def ShutDown(self):
        self.RunTask("HP.Common.Services.StateSchedulerTask", "shutdown", None)
        
    def SignalActivity(self):
        """
        Signal Activity
        """
        self.RunTask("RisDeviceTask","signalactivity", None)
    
    def SnmpChangeOIDAccessPermission(self, oid, access):
        """Changes OID access using RemoteInvocationService
        :param oid: OID to change
        :param access: desired access for oid which are
            "ReadOnly"
            "WriteOnly"
            "readWrite"
            "ReadOnlyTrappable"
            "ReadWriteTrappable"
            "NotAccessible"
        :return: True or False to indicate success of change
        
        :example:
        rt = RemoteTaskProxy(dut.RemoteTask)
        flag = rt.SnmpChangeOIDAccessPermission("1.4.1.9.51","ReadOnly")
        """
        setArgs = [oid, access]
        return self.RunTask("PmlToSnmpTask", "snmpchange", setArgs)
        
    def SnapShot(self):
        """
        It will take a snapshot of Control Panel and return the path where it is 
        stored on the unit. 
        """
        return self.RunTask("RisWindowsTask", "snapshot", None)
        
    def GetSpiNvpBatch(self, nvps):
        """
        RisGetNameValueBatch retrieves a list of Name Value Pairs 
        @param nvps: List of NVPs to retrieve 
        @return: a List of NVPS with the corresponding values
        """
        # loop thru and create xml get request
        reqCreator = RisNVPXmlRequestCreator()
        for nvp in nvps:
            reqCreator.AddGetElement(nvp.Guid, nvp.Name)
        xmlReqData = reqCreator.GenerateXml()
        log.debug("XML Get Request Data " + xmlReqData)
        
        # Send Request
        setArgs = [xmlReqData]
        xmlRetData = self.RunTask("RisDeviceTask","nvramgetbatch", setArgs)
        log.debug("Returned NVP Values ********\n\n" + xmlRetData)
        
        # Parse out Data
        listOfValues = RisNVPXmlResponseParser.Parse(xmlRetData)
        log.debug(str.format("NVPs Req Length {0} NVPs Res Length {1} ",len(nvps),len(listOfValues)))
        for i in range(len(listOfValues)):
            if listOfValues[i] == "":
                nvps[i].HexValue = ""
                nvps[i].Value = ""
            else:
                nvps[i].HexValue = listOfValues[i]
            
        return nvps
        
    def SetSpiNvpBatch(self, nvps):
        """
        RisSetNameValueBatch performs one set call on the list of nvps
        @param nvps: The list of Name Value Pairs
        @return: void
        """

        #loop thru and create xml set request
        reqCreator = RisNVPXmlRequestCreator()
        for nvp in nvps:
            reqCreator.AddSetElement(nvp.Guid, nvp.Name, nvp.HexValue)
        xmlReqData = reqCreator.GenerateXml()
        log.debug("XML Set Request Data " + xmlReqData)
        
        #send the xml set request
        setArgs = [xmlReqData]
        self.RunTask("RisDeviceTask","nvramsetbatch",setArgs)
        
    def SetSpiNvpValue(self, guid, name, value):
        """
        RisSetNameValuePair sets a Name Value 
        @param guid: The guid of the variable name
        @param name: The variable name
        @param value: The value to set variable Name
        """
        setArgs = [guid,name,value]
        self.RunTask("RisDeviceTask","nvramset", setArgs)

    def GetSpiNvpValue(self, guid, name):
        """
        RisGetNameValue returns the string value of Name Value pair. It utilizes a NameValueVar
        object from a lookup table, which includes methods to convert hexstring to string on 
        assignment. That is, assign nvVar.HexValue will automatically generate nvVar.Value string
        that is returned.    
        @param guid: The guid of the variable name
        @param name: The variable name
        @return: The value from variable Name
        """
        
        getArgs = [guid,name]
        value = self.RunTask("RisDeviceTask","nvramget", getArgs)
        return value
        
    def SetIcbNvpValue(self, guid, name, value):
        """
        RisSetNameValuePair sets a Name Value 
        @param guid: The guid of the variable name
        @param name: The variable name
        @param value: The value to set variable Name
        """
        setArgs = [guid,name,value]
        self.RunTask("RisDeviceTask","icbset", setArgs)

    def GetIcbNvpValue(self, guid, name):
        """
        RisGetNameValue returns the string value of Name Value pair. It utilizes a NameValueVar
        object from a lookup table, which includes methods to convert hexstring to string on 
        assignment. That is, assign nvVar.HexValue will automatically generate nvVar.Value string
        that is returned.    
        @param guid: The guid of the variable name
        @param name: The variable name
        @return: The value from variable Name
        """
        getArgs = [guid,name]
        value  = self.RunTask("RisDeviceTask","icbget", getArgs)
        return value

    def DeletetAllSpiNVPsForGuid(self, guid):
        """
        RisDeleteNameValuePair Deletes all name value pairs
        that match the guid from the name passed in.
        @param guid: The guid of the variable
        """
        return self.RunTask("RisFimTask","deletenvramvariableforguid",[guid])
        
    def DeleteSpiNvp(self, guid, name):
        """
        RisDeleteNameValuePair Deletes all name value pairs
        that match the guid from the name passed in.
        @param guid: The guid of the variable
        """
        deleteArgs = [guid,name]
        return self.RunTask("RisFimTask","deletenvramvariableforguidname",deleteArgs)

    def SimUsbGetThumbDrives(self):
        """
        return the list of USB thumbdrives present 
        @return: list
        """
        class SimUsbDevice(object):
            def __init__(self, path, volume):
                self.Path = path
                self.Volume = volume

        taskName = "HP.Mfp.HardwareServices.SimulationDeviceFinder"
        data = self.RunTask(taskName,"Get",None)
        tokens = data.split('|')
        if len(tokens) < 2:
            return []
        usbDevices = []
        for i in range(0,len(tokens),2):
            print("len(tokens) = ", len(tokens))
            s = SimUsbDevice(tokens[i],tokens[i + 1])
            usbDevices.append(s)
        return usbDevices
    
    def SimUsbRemoveDevice(self,path = r"\FalconUsbDrive", volumeName = "FalconUsbDrive"):
        """
        Removes the specific usb device at path and volume location
        path - the USB thumbdrive path defaults to UsbSimulation\DSThumbDriveA
        volume - the volumen name defaults to "Sim Usb Stick"
        """
        taskName = "HP.Mfp.HardwareServices.SimulationDeviceFinder"
        args = [volumeName,path]
        installedDevides = self.SimUsbGetThumbDrives()
        if len([x for x in installedDevides if x.Path == path and x.Volume == volumeName]):
            log.debug(str.format("Removing {0} {1}", volumeName, path))
            self.RunTask(taskName,"Remove",args)
        
    def SimUsbInstallDevice(self,path = r"\FalconUsbDrive", volumeName = "FalconUsbDrive"):
        """
        Installs a simulated USB thumbdrive at path and volume locations
        path - the USB thumbdrive path defaults to UsbSimulation\DSThumbDriveA
        volume - the volumen name defaults to "Sim Usb Stick"
        """
        usbDevice = "thumbdrive"
        state = "null"
        taskName = "HP.Mfp.HardwareServices.SimulationDeviceFinder"
        args = [path,usbDevice,volumeName,state]
        return self.RunTask(taskName,"Add",args)

class RisNVPXmlRequestCreator(object):
    def __init__(self):
        self._data = ""
    def AddGetElement(self, guid, name):
        self._data = self._data + str.format("<Request><CategoryId>{0}</CategoryId><Variable>{1}</Variable></Request>",guid,name)
    
    def AddSetElement(self, guid, name, hexValue):
        self._data = self._data + str.format("<Request><CategoryId>{0}</CategoryId><Variable>{1}</Variable><Value>{2}</Value></Request>",guid,name, hexValue)
        
    def GenerateXml(self):
        return str.format("<Requests>{0}</Requests>", self._data)
        
    def Clear(self):
        self._data = ""

class RisNVPXmlResponseParser(object):
    @staticmethod
    def Parse(xmlRetData):
        """
        Parse response XML data and returns a list of values
        """
        tokenStart = "<Response>"
        tokenEnd = "</R"
        indexStart = 0
        indexEnd = 0
        data = []
        while True:
            indexStart = xmlRetData.find(tokenStart,indexEnd)
            if indexStart == -1:
                break
            indexEnd = xmlRetData.find(tokenEnd,indexStart)
            if indexEnd == -1:
                break
                
            if (indexStart + len(tokenStart)) == indexEnd:
                data.append("")
            else:
                data.append(xmlRetData[indexStart + len(tokenStart):indexEnd])
            
        return data