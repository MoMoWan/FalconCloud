"""
ledm.set_io_type("USB", port_name = None)
ledm_set-Io_type("LAN", ipaddress="10.1.1.100")
mfg_tree = ledm.get("ManufacturingConfigDyn")

mfg_settable_tree = ledm.trees.ManufacturingConfigDyn()
mfg_seettable_tree.node = value
ledm.put(mfg_settable_tree)

#session based 

with ledm.Session() as session:
    session.get
    session.put
    session.get
    session.put


# how do we fax self fax test

"""
# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

import time
import requests
from requests.auth import HTTPBasicAuth
from . import ledm_io
from . import ledm_session
from . import resource


MFG_PASSWORD = "HPBoiseFSN"

def get(tree_name):
    """
    This will get Ledm Tree
    Args:
        tree_name (str): Tree Name or resource path

    Returns:
        LedmClass: The LEDM class for Tree
    """    
    tree_path = resource.TREES_URI[tree_name]
    tree_path = "/" + tree_path if not tree_path.startswith("/") else tree_path
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    log.debug("GET {}".format(url))
    with ledm_session.LedmSession() as session:
        headers = {'Content-type': r'text/xml'}
        response = session.get(url, headers=headers)
        if response.status_code == requests.codes.ok:
            return resource.TREE_MAPPING_TO_OBJECT[tree_name](response.text)
        else:
            log.debug("response.status_code = {}".format(response.status_code))
            response.raise_for_status()

def get_with_status_code(tree_name):
    """
    This will get Ledm Tree
    Args:
        tree_name (str): Tree Name or resource path

    Returns:
        LedmClass: The LEDM class for Tree
    """    
    tree_path = resource.TREES_URI[tree_name]
    tree_path = "/" + tree_path if not tree_path.startswith("/") else tree_path
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    log.debug("GET {}".format(url))
    with ledm_session.LedmSession() as session:
        headers = {'Content-type': r'text/xml'}
        response = session.get(url, headers=headers)
        if response.status_code == requests.codes.ok:
            return response.status_code, resource.TREE_MAPPING_TO_OBJECT[tree_name](response.text)
        else:
            return response.status_code, None

def update(tree_name, data):
    """
    Wrapper around put
    """
    return put(tree_name, data)


def put(tree_name, data, timeout=2):
    """
    This will perform a LEDM PUT with data
    """
    tree_path = resource.TREES_URI[tree_name]
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    log.debug("put {}".format(url))
    data = str(data)
    mfg_pass_required = False
    if any([tree_password.upper() in tree_name.upper() for tree_password in resource.TREES_MFG_PASSWORD]):
        mfg_pass_required = True
    log.debug("mfg_pass_required = {}".format(mfg_pass_required))
    with ledm_session.LedmSession() as session:
        if mfg_pass_required:
            log.debug("PASSWORD = {}".format(MFG_PASSWORD))
            headers = {'Content-type': r'text/xml'}
            response = session.put(url, data=data, headers=headers, auth=HTTPBasicAuth("", MFG_PASSWORD), timeout=timeout)
            if response.status_code == 401:
                response = _resend_put_for_updated_password(url, data, session)
            if response.status_code == 510:
                time.sleep(.2)
                response = session.put(url, data=data, auth=HTTPBasicAuth("", MFG_PASSWORD), timeout=timeout)
        else:    
            headers = {'Content-type': r'text/xml'}
            response = session.put(url, data=data, headers=headers, timeout=timeout)
            if response.status_code == 510:
                response = session.put(url, data=data)
        if response.status_code != requests.codes.ok:
            log.debug("response.status_code = {}".format(response.status_code))
            response.raise_for_status()

def _resend_put_for_updated_password(url, data, session):
    global MFG_PASSWORD
    mfg = get("ManufacturingConfigDyn")
    MFG_PASSWORD = "HPBoise" + mfg.formatter_serial_number
    log.debug("PASSWORD = {}".format(MFG_PASSWORD))
    headers = {'Content-type': r'text/xml'}
    return session.put(url, data=data, headers=headers, auth=HTTPBasicAuth("", MFG_PASSWORD))

def create(tree_name, data):
    """
    Wrapper around post
    """
    return post(tree_name, data)

def post(tree_name, data):
    """
    This will perform a LEDM POST with data
    """
    tree_path = resource.TREES_URI[tree_name]
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    with ledm_session.LedmSession() as session:
        headers = {'Content-type': r'text/xml'}
        response = session.post(url, data=data, headers=headers)
        if response.status_code not in (200, 201, 202):
            log.debug("response.status_code = {}".format(response.status_code))
            response.raise_for_status()
        return response.headers

def head(tree_name):
    """
    This will perform a HTTP HEAD with url

    Args:
        tree_name (str): The name of the tree of resource path

    Returns:
        pass 
    """
    tree_path = resource.TREES_URI[tree_name]
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    with ledm_session.LedmSession() as session:
        response = session.head(url)
        return response

def is_available(time_to_wait, tree_name="ManufacturingConfigDyn"):
    """
    This will determine if tree is available, the default
    tree is the ManufacturingConfigDyn.

    Args:
        time_to_wait (int): how much time to wait for service
        tree_name (str): the name of the tree default DiscoveryTree

    Returns:
        bool: True if service is available and False is not available. 
    """
    start_time = time.time()
    while (time.time() - start_time) < float(time_to_wait):
        try:
            status_code, response = get_with_status_code(tree_name)
            if status_code == 200:
                return True
        except IOError:
            pass

    return False