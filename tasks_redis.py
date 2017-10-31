import os
import binascii
import logging
import json
import  tornado.escape
from celery import Celery, utils,result
import time
import ledm
import jedilib
import fim_util

broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'
logger = logging.getLogger('celery')
task_log = utils.log.LoggingProxy(logger)
app = Celery('my_task', broker=broker, backend=backend)


import globals
root_dir = os.path.dirname(os.path.abspath(__file__))
globals.BIN_DIRECTORY = os.path.join(root_dir, "bin")


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

    # special NVP CLEAR_ALL_DATA to indicate a special case
    clear_all_data = False
    for nvp in nvps:
        if "CLEAR_ALL_DATA" in nvp[1].upper():
            clear_all_data = True
            continue
        nvps_data.append(NvpVar(
            guid=nvp[0],
            name=nvp[1],
            data_type=nvp[2],
            value=nvp[3]
            ))
    remote_task_service = jedilib.RunTaskService(ip_address)
    if not remote_task_service.is_available(5):
        task_log.write("RS not available sending fim bundle")
        try:
            fim_util.enable_production_services(ip_address,user_name, password)
        except Exception as ex:
            pass
        if not remote_task_service.is_available(5):
            if user_name != "admin" and password != "":
                fim_util.enable_production_services(ip_address,"admin", "")
        else:
            task_log.write("service is available")
    else:
        task_log.write("service is available")
    if clear_all_data:
        task_log.write("clearing all data")
        remote_task_service.clear_all_data()
    remote_task_service.set_spi_nvp_batch(nvps_data)

@app.task
def send_fim_bundle_task(ip_address, bundle_file_path, user_name="admin", password=""):
    """
    This will send a fim bundle

    Args:
        ip_address (str): The printer ip address
        bundle_file_path (str):  fim bundle path
        user_name (str): Printer user name
        password (str):  Printer password
    """
    task_log.write("printer ip_address {} bundle {} user_name {} password {}".format(
        ip_address,
        bundle_file_path,
        user_name,
        password))
    # check if user_name and password is correct
    temp_bundle = os.path.join(globals.BIN_DIRECTORY, "test.bdl")
    try:
        task_log.write("temp_bundle = {}".format(temp_bundle))
        fim_util.send_fim_bdl(ip_address,temp_bundle, user_name, password)
    except Exception as ex:
        task_log.write("Username Exception type {}".format(type(ex)))
        task_log.write("Checking if username is admin == {}".format(user_name))
        if "admin" != user_name:
            user_name = "admin"
            password = ""
            task_log.write("new user_name {} password {}".format(user_name, password))
            fim_util.send_fim_bdl(ip_address,temp_bundle, user_name, password)
        else:
            task_log.write("Unknown username and password credentials")
            raise
    task_log.write("FIM BDL user_name {} password {}".format(user_name, password))
    fim_util.send_fim_bdl(ip_address,bundle_file_path,user_name,password)

@app.task
def ledm_set(ip_address,jsondata,timeout=30):
    """
    This will set LEDM trees

    Args:
        ip_address(str): The printer IP
        ledm_section(dic): the ledm data is a dic data like - {tree name:[{node_name:node_value}] }

    """
    jsondata =  json.dumps(jsondata)
    jsondata = tornado.escape.json_decode(jsondata)
    ledm.set_io(ip_address)
    ledm.set_http_scheme("HTTP")
    for section in jsondata:
        if section != "printer":
            task_log.write("LEDM Section {}".format(section))
            tree = ledm.create_settable_model(section)
            for node in jsondata[section]:
                for nodename, nodevalue in node.items() :
                    tree.set(nodename, nodevalue)
                    task_log.write("LEDM set {}  {}".format(nodename, nodevalue))
            ledm.put(section, tree, timeout)