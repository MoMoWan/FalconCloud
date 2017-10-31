"""
This is specific functions for udw commands
"""

import logging
log = logging.getLogger(__name__)

import urllib
import requests
from . import ledm_io
from . import ledm_session

def send_udw(udw_cmds, timeout=None):
    """
    This will send udw command via session-less
    via REST interface. 

    Args:
        udw_cmds (str|list): a single or list of udw commands
        timeout (int): if not None it will set the timouet

    Returns:
        str|list: either response code or list of responses
    """
    return _get(udw_cmds, timeout)

def _get(udw_cmds, timeout=None):
    """
    Inner command to send udw commands over the REST
    interface. 

    Args:
        udw_cmds (str|list): a single or list of udw commands
        timeout (int): if not None it will set the timouet

    Returns:
        str|list: either response code or list of responses
    """
    url, is_not_str = _create_url(udw_cmds, timeout)
    log.debug("GET {}".format(url))
    with ledm_session.LedmSession() as session:
        headers = {'Content-type': r'text/xml'}
        response = session.get(url, headers=headers)
        if response.status_code == requests.codes.ok:
            if "BAD_CMD" in response.text:
                raise ValueError("{} command not valid".format(udw_cmds))
            if is_not_str:
                return response.text.split(";")
            else:
                return response.text
        else:
            log.debug("response.status_code = {}".format(response.status_code))
            response.raise_for_status()

def _create_url(udw_cmds, timeout=None):
    is_not_str = False
    if not isinstance(udw_cmds, str):
        is_not_str = True
        udw_cmds = "".join(udw_cmds)
    query_string = urllib.parse.quote_plus(udw_cmds)
    if timeout:
        query_string += "&timeout={}".format(timeout)
    tree_path = r"/UDW/Command?entry=udw.error_token+BAD_CMD;" + query_string
    url = "{}{}{}".format(ledm_io.HTTP_SCHEME, ledm_io.HTTP_HOST, tree_path)
    return url, is_not_str