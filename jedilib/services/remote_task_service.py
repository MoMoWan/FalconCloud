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
# logging
# =============================================================================
import logging
log = logging.getLogger("run_task")


# =============================================================================
# Standard Python modules
# =============================================================================
from .message import RisSoapMessage
from .soap.client import SoapClient
from .soap import SoapFaultException
import os
import time
import binascii


# =============================================================================
# Globals and Definitions
# =============================================================================




# =============================================================================
# Falcon Python modules
# =============================================================================
class RemoteTask(object):
    CURRENT_SERVICE = "controlpanel"
    NEXT_SERVICE = {
        "controlpanel":"remoteuserinterface", 
        "remoteuserinterface":"controlpanel"
    }

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.soap_client = SoapClient(self.ip_address,port=65102,service="remoteinvocation",is_secure=False)
        
        
    def run_task(self, task_name, method_identifier, parameters = None):
        """
        Tells the RemoteInvocationService to execute an IQualificationTask RunTask 
        that is in Jedi.
      
        Args:
        taskName (str) - the name of the IQualificationTask running on the device
        methodIdentifier (str) - if the task has multiple subtasks each subtask will be identified by the optional methodIdentifier
        parameters (list)- list of any optional string parameters that the task expects
        
        Returns:
            (str)- string response from the RunTask
        """
        response = None
        msg = RisSoapMessage(task_name, method_identifier, parameters, self.ip_address, RemoteTask.CURRENT_SERVICE).tostring()
        log.debug(msg)
        try:
            response = self.soap_client(msg)
        except SoapFaultException as ex:
            log.debug("Faul Exception in {}".format(ex))
            if "cannot be processed at the receiver" in str(ex):
                service = RemoteTask.NEXT_SERVICE[RemoteTask.CURRENT_SERVICE]
                log.debug("service is {}".format(service)
                )
                msg = RisSoapMessage(task_name, method_identifier, parameters, self.ip_address, service).tostring()
                response = self.soap_client(msg)                
                log.debug("Switching service endpoint from {} to {}".format(RemoteTask.CURRENT_SERVICE, service))
                RemoteTask.CURRENT_SERVICE = service
        return response
        
        
        
    def clear_all_data(self):
        """
        Clears Customer, Machine, and extensibility data on the device
        """
        args = None
        self.run_task("RisDeviceTask", "clearalldata", args)
        
    def clear_customer_data(self):
        """
        Clears Customer data on the device
        """
        args = None
        self.run_task("RisDeviceTask", "clearcustomerdata", args)
        
    def create_file_on_read_only_partition(self, fileName, partition, text):
        """
        creates a file on a read only partition
        fileName - The file to create on the partition
        partition - the partition to create the file on, like PREBOOT
        text - the text to write to the file after creating it
        """
        args = [fileName, partition, text]
        self.run_task("StorageManagerTask", "CreateFileOnReadOnlyPartition", args)
        
    def bread_crumb(self):
        """
        return UI BreadCrumb 
        """
        return self.run_task("RisDeviceTask","breadcrumb", None)
        
    def clear_all_data(self):
        return self.run_task("RisDeviceTask","clearalldata", None)

    def clear_ring_buffer(self):
        """
        It will clear out the ring buffer
        """
        self.run_task('ComponentManagerTask','ClearAllRingBuffers', None) 
        
    def control_panel_status(self):
        return self.run_task("RisDeviceTask","controlpanelstatus", None)

    def deletet_all_spi_nvps_for_guid(self, guid):
        """
        RisDeleteNameValuePair Deletes all name value pairs
        that match the guid from the name passed in.
        @param guid: The guid of the variable
        """
        return self.run_task("RisFimTask","deletenvramvariableforguid",[guid])

    def delete_spi_save_recover_guid_id_nvp(self, guid = "D2B9F4DC-B3BD-47a9-8444-46B6D8338778"):
        """
        Delete SPI Save Recover ID ManufSRClientSpiStorageId
        D2B9F4DC-B3BD-47a9-8444-46B6D8338778,ManufSRClientSpiStorageId

        Args:
            guid (str): GUID for SPI Save Recover ID
        """
        self.deletet_all_spi_nvps_for_guid("D2B9F4DC-B3BD-47a9-8444-46B6D8338778")

    def delete_all_spi_nvps_for_guid(self, guid):
        """
        RisDeleteNameValuePair Deletes all name value pairs
        that match the guid from the name passed in.
        @param guid: The guid of the variable
        """
        return self.run_task("RisFimTask","deletenvramvariableforguid",[guid])
    
    def delete_file_on_read_only_partition(self, fileName, partition):
        """
        Deletes a file on a read-only partition
        fileName - The file to delete on the partition
        partition - The partition to delete the file, like PREBOOT
        """
        args = [fileName, partition]
        self.run_task("StorageManagerTask", "DeleteFileOnReadOnlyPartition", args)
        
    def delete_spi_nvp(self, guid, name):
        """
        RisDeleteNameValuePair Deletes all name value pairs
        that match the guid from the name passed in.
        @param guid: The guid of the variable
        """
        deleteArgs = [guid,name]
        return self.run_task("RisFimTask","deletenvramvariableforguidname",deleteArgs)

    def get_event_log_entry_count(self):
        """
        Get event log entry count for error, warning, and info
        """
        class EventLogEntryCount(object):
            def __init__(self, errorCount, warningCount, infoCount):
                self.ErrorCount = errorCount
                self.WarningCount = warningCount
                self.InfoCount = infoCount
                
        errorCount = self.run_task('RisDeviceTask', 'GetEventLogEntryCount', ["error"])
        warningCount = self.run_task('RisDeviceTask', 'GetEventLogEntryCount', ["warning"])
        infoCount = self.run_task('RisDeviceTask', 'GetEventLogEntryCount', ["info"])
        return EventLogEntryCount(errorCount, warningCount, infoCount)

    def get_error_log_entries(self):
        return self.run_task("RisDeviceTask", "geterrorlogentries", None)
    
    def get_execution_mode(self, guid="0429E79E-D9BA-412E-A2BC-1F3d245041CE"):
        """
        Gets the falcon jedi state

        Args:
            guid (str): The guid for ExecutionMode NVP

        Returns:
            str : The string value of ExecutionMode
        """
        value = self.get_spi_nvp_value(guid, "ExecutionMode")
        return binascii.unhexlify(value).decode()
        
    def get_falcon_jedi_state(self, guid="D7BFA98C-6389-4661-8ED2-FC3775A800E0"):
        """
        Gets the falcon jedi state

        Args:
            guid (str): The guid for FalconJediState NVP

        Returns:
            str : The string value of FalconJediState
        """

        return self.get_spi_nvp_value(guid, "FalconJediState")

    def get_icb_nvp_value(self, guid, name):
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
        value  = self.run_task("RisDeviceTask","icbget", getArgs)
        return value

    def get_inactivity_timeout(self):
        return int(self.run_task("HP.Mfp.App.ControlPanel.Framework.ControlPanelUtilitiesTask","GetInactivityTimeout", None))
        
    def get_led_ready(self):
        """
        Get the State of the Ready LED it is either on or off
        """
        return self.run_task("LedProviderTask", "ReadyLed", None)
        
    def get_led_data(self):
        """
        Get the State of the Data LED it is either on or off
        """
        return self.run_task("LedProviderTask", "DataLed", None)
        
    def get_led_attention(self):
        """
        Get the State of the Attention LED it is either on or off
        """
        return self.run_task("LedProviderTask", "AttentionLed", None)

    def get_ring_buffers(self):
        """
        returns the string contents of the ring buffer
        """
        return self.run_task('ComponentManagerTask','DumpAllRingBuffers', None) 

    def get_secure_disk_status(self, guid="E8D56211-1010-4A25-B6AB-D1AB7E98A217"):
        """
        Gets the NVP SecureDiskStatus Status

        Args:
            guid (str): The guid of SecureDiskStatus

        Returns:
            str : The hex string value of SecureDiskStatus
        """
        return self.get_spi_nvp_value(guid,"SecureDiskStatus")

    def get_spi_nvp_value(self, guid, name):
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
        value = self.run_task("RisDeviceTask","nvramget", getArgs)
        return value

    def get_spi_nvp_batch(self, nvps):
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
        xmlRetData = self.run_task("RisDeviceTask","nvramgetbatch", [xmlReqData])
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
        
    def is_available(self, time_to_wait, timeToDelay = 1):
        """
        It checks if RIS is available within time_to_wait seconds
        """
        start = time.time()
        log.info("Waiting For RIS  for " + str(time_to_wait))  
        while ((time.time() - start) < int(time_to_wait)):
            try:
                self.run_task("RisDeviceTask", "geterrorlogentries", None)
                return True
            except:
                log.exception("Error occurred")
                log.info("Waiting For RIS : " + str(curTime) + " of " + str(time_to_wait)) 
                time.sleep(int(timeToDelay))
                continue
                
        return False
        
    def reboot(self):
        self.run_task("HP.Common.Services.StateSchedulerTask", "requestreboot", None)

    def set_inactivity_timeout(self, value):
        v = [str(value)]
        return self.run_task("HP.Mfp.App.ControlPanel.Framework.ControlPanelUtilitiesTask","SetInactivityTimeout", v)

    def set_falcon_jedi_state(self, value, guid="D7BFA98C-6389-4661-8ED2-FC3775A800E0"):
        """
        Gets the falcon jedi state

        Args:
            value (str): The value to set Falcon Jedi State
            guid (str): The guid for FalconJediState NVP

        """
        v = binascii.hexlify(value.encode()).decode()
        log.debug("Set Value {} Hex Value {} ".format(value, v))        
        self.set_spi_nvp_value(guid,"FalconJediState", v)
                    
    def shutdown(self):
        self.run_task("HP.Common.Services.StateSchedulerTask", "shutdown", None)
        
    def signal_activity(self):
        """
        Signal Activity
        """
        self.run_task("RisDeviceTask","signalactivity", None)
    
    def snap_shot(self):
        """
        It will take a snapshot of Control Panel and return the path where it is 
        stored on the unit. 
        """
        return self.run_task("RisWindowsTask", "snapshot", None)

    def snmp_change_oid_access_permission(self, oid, access):
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
        return self.run_task("PmlToSnmpTask", "snmpchange", [oid, access])
                
    def set_spi_nvp_batch(self, nvps):
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
        self.run_task("RisDeviceTask","nvramsetbatch",setArgs)
        
    def set_spi_nvp_value(self, guid, name, value):
        """
        RisSetNameValuePair sets a Name Value 
        @param guid: The guid of the variable name
        @param name: The variable name
        @param value: The value to set variable Name
        """
        setArgs = [guid,name,value]
        self.run_task("RisDeviceTask","nvramset", setArgs)
    
    def set_icb_nvp_value(self, guid, name, value):
        """
        RisSetNameValuePair sets a Name Value 
        @param guid: The guid of the variable name
        @param name: The variable name
        @param value: The value to set variable Name
        """
        setArgs = [guid,name,value]
        self.run_task("RisDeviceTask","icbset", setArgs)

    def sim_usb_get_thumb_drives(self):
        """
        return the list of USB thumbdrives present 
        @return: list
        """
        class SimUsbDevice(object):
            def __init__(self, path, volume):
                self.Path = path
                self.Volume = volume

        taskName = "HP.Mfp.HardwareServices.SimulationDeviceFinder"
        data = self.run_task(taskName,"Get",None)
        tokens = data.split('|')
        if len(tokens) < 2:
            return []
        usbDevices = []
        for i in range(0,len(tokens),2):
            print("len(tokens) = ", len(tokens))
            s = SimUsbDevice(tokens[i],tokens[i + 1])
            usbDevices.append(s)
        return usbDevices
    
    def sim_usb_remove_device(self,path = r"\FalconUsbDrive", volumeName = "FalconUsbDrive"):
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
            self.run_task(taskName,"Remove",args)
        
    def sim_usb_install_device(self,path = r"\FalconUsbDrive", volumeName = "FalconUsbDrive"):
        """
        Installs a simulated USB thumbdrive at path and volume locations
        path - the USB thumbdrive path defaults to UsbSimulation\DSThumbDriveA
        volume - the volumen name defaults to "Sim Usb Stick"
        """
        usbDevice = "thumbdrive"
        state = "null"
        taskName = "HP.Mfp.HardwareServices.SimulationDeviceFinder"
        args = [path,usbDevice,volumeName,state]
        return self.run_task(taskName,"Add",args)

class RisNVPXmlRequestCreator(object):
    def __init__(self):
        self._data = ""
    def add_get_element(self, guid, name):
        self._data = self._data + str.format("<Request><CategoryId>{0}</CategoryId><Variable>{1}</Variable></Request>",guid,name)
    
    def add_set_element(self, guid, name, hexValue):
        self._data = self._data + str.format("<Request><CategoryId>{0}</CategoryId><Variable>{1}</Variable><Value>{2}</Value></Request>",guid,name, hexValue)
        
    def generate_xml(self):
        return str.format("<Requests>{0}</Requests>", self._data)
        
    def clear(self):
        self._data = ""

class RisNVPXmlResponseParser(object):
    @staticmethod
    def parse(xmlRetData):
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