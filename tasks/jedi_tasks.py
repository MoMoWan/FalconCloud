
import binascii
import logging
import json
from celery import Celery, utils,result
import time
import jedilib

broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'
logger = logging.getLogger('celery')
task_log = utils.log.LoggingProxy(logger)
app = Celery('my_task', broker=broker, backend=backend)


class NvpVar:
    """
    This will mock up the NvpVar that lower level
    library is expecting
    """
    def __init__(self, guid, name, data_type, value):
        """
        This will initialize POCO data NvpVar

        Args:
            guid (str): The nvp GUID
            name (str): The nvp name
            data_type(str): hex or str data types
            value (str): the value either hex or str
        """
        self.Guid = guid
        self.Name = name
        if data_type.lower() == "hex":
            self.HexValue = value
        else:
            self.HexValue = binascii.hexlify(value.encode()).decode().upper()

@app.task
def nvp_sets(ip_address, nvps, user_name="admin", password=""):
    """
    This will set the nvps for a unit with ip_address. The default
    user_name and password is admin and ""

    The NVP will look like this
    ["845E3285-C67C-4F4B-9AA4-0AE91BD35089",
    "JDIMfgReset",
    "hex",
    "01000000"]

    Args:
        ip_address (str): The printer ip address
        nvps ([nvps]): a list of nvps
        user_name (str): Printer user name
        password (str):  Printer password
    """
    # loop thru and convert to convert format
    nvps_data= []
    task_log.write("JS_Data: " + ip_address + ";" +user_name +";"+password)
    for nvp in nvps:
        #task_log.write("nvp[0] " + nvp[0])
        #task_log.write("nvp[1] " + nvp[1])
        #task_log.write("nvp[2] " + nvp[2])
        #task_log.write("nvp[3] " + nvp[3])
        nvps_data.append(NvpVar(
            guid=nvp[0],
            name=nvp[1],
            data_type=nvp[2],
            value=nvp[3]
            ))
    remote_task_service = jedilib.RunTaskService(ip_address)
    remote_task_service.set_spi_nvp_batch(nvps_data)
    #remote_task = jedilib.RemoteTask(ip_address)
    #remote_task.SetSpiNvpBatch(nvps_data)
 