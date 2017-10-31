import clr
clr.AddReference('HP.Falcon.Jedi')
from HP.Falcon.Jedi.FIM import *
from HP.Falcon.Jedi.FIM.Bundle import *
from System.IO import File
import jedilib
import tempfile
import globals
import datetime
import os
import sys
import shutil


import logging
log = logging.getLogger(__name__)

import globals
root_dir = os.path.dirname(os.path.abspath(__file__))
globals.BIN_DIRECTORY = os.path.join(root_dir, "bin")


def enable_production_services(ip_address, username="admin", password=""):

    support_key, formatter_sn, bdl_data_code = ews_get_config_bdl_required_vars(ip_address)

    bdl_file_path = create_mfg_bdl_file(support_key, formatter_sn, bdl_data_code)

    send_fim_bdl(ip_address, bdl_file_path, username, password)

def ews_get_config_bdl_required_vars(ip_address):
    '''
    It returns [SupportKey,FormatterSN,BundleDateCode] to generate the Manufacturing
    BDL
    @return: list [SupportKey,FormatterSN,BundleDateCode]
    '''
    ewsProxy = jedilib.Ews(ip_address)
    if not ewsProxy.wait_for_ews_ready(30):
        msg = str.format("EWS HTTP GET Failed for ip Address {0}", ewsProxy.ip_address)
        raise Exception(msg)

    configValues = ewsProxy.get_config_page_values()
    supportKey = configValues["SupportKey"]
    log.debug("SupportKey " + supportKey)
    formatterSN = configValues["FormatterNumber"]
    log.debug("Formatter Serial Number " + formatterSN)
    #bundleDateCode = time.strftime("%m/%d/%Y",time.localtime())
    #Bundle Build Date good for current printer date and 30 days in future
    #Create Date that is 2 days old for margin since the printer clock can be off by +/- 1 day
    then = datetime.date.today() - datetime.timedelta(days=2)
    bundleDateCode = then.strftime("%m/%d/%Y")
    log.debug("Bundle Date Code " + bundleDateCode)
    return [supportKey,formatterSN,bundleDateCode]

def create_mfg_bdl_file(support_key, formatter_sn, bdl_data_code):
    '''
    It creates a creates Manufacturing BDL
    <Product>\bin\Tools is the location where it will Tools
    '''
    temp_dir = tempfile.mkdtemp()
    payLoadData = _CreateSignAndEncryptedData(support_key, formatter_sn, bdl_data_code)
    payload_path = os.path.join(temp_dir,"SecurePayload.dat")
    log.debug("Save Secure Payload to " + payload_path)
    File.WriteAllBytes(payload_path,payLoadData)
    #File.WriteAllBytes(payload_path,payLoadData)
    # Check existence of each path
    log.debug("Save Secure Manufacturing BDL to " + temp_dir)
    tool_bin = globals.BIN_DIRECTORY
    log.debug("Bin Directory = {}".format(tool_bin))
    return _CreateBdlFile(tool_bin,payload_path, temp_dir)

def send_fim_bdl(ip_address, bdl_file_path, user_name="admin", password=""):
    # create temp directory
    temp_dir = tempfile.mkdtemp()
    temp_bundle_path = os.path.join(temp_dir, "bundle.bdl")
    shutil.copy2(bdl_file_path, temp_bundle_path)
    log.debug(str.format("{0} being sent to FIM web service",temp_bundle_path))
    fim = jedilib.Fim(ip_address)
    fim.download(temp_bundle_path, user_name, password)

def _CreateSignAndEncryptedData(supportKey,formatterSN,bundleDateCode):
    '''
    It will create a sign and encrypted payload that will enable CTF
    '''
    signingProxy = ConfigSigningProxy()
    data = signingProxy.CreateSecurePayLoad(supportKey,formatterSN,bundleDateCode)
    return data

def _CreateBdlFile(tool_bin, secure_data_path, output_path):
    print("tool_bin {} secure_data_path = {} output_path = {}".format(tool_bin, secure_data_path, output_path))
    bdlCreator = BdlCreator(tool_bin)
    return bdlCreator.CreateConfigBdlFromCvsFile(secure_data_path,output_path)
