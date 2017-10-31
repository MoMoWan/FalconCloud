import logging
log = logging.getLogger(__name__)

import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
    

class SoapFaultException(Exception):
    pass

class cached_property(object):
    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result

class SoapClient(object):

    """SOAP client."""

    def __init__(self, ip_address, port, service, is_secure=False, **kwargs):
        """Set base attributes."""
        self.ip_address = ip_address
        self.port = port
        self.service = service
        self.is_secure = is_secure
        

    @cached_property
    def _session(self):
        """Cached instance of requests.Session."""
        return requests.Session()

    def __call__(self, msg, user="admin", password=""):
        """Post 'msg' to remote service."""
        # generate HTTP request from msg
        url = "http{}://{}:{}/{}".format(
            "s" if self.is_secure else "",
            self.ip_address,
            self.port,
            self.service
            )

        log.debug(url)
        basic_auth = HTTPBasicAuth(user, password)
        # perform HTTP(s) POST
        resp = self._session.post(
            url,
            auth=basic_auth,
            headers={
                "Accept-Encoding":"gzip, deflate",
                "Content-Type":"application/soap+xml; charset=utf-8",
                "Content-Length":str(len(msg)),
                "Expect":"100-continue"
                }, 
            data=msg, 
            verify=False)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        log.debug(resp.content)
        soap_data = BeautifulSoup(resp.content, "xml")
        body = soap_data.find("Body")
        if soap_data.find("Fault"):
            raise SoapFaultException(str(next(body.children)))
        if body is None:
            return ""
        else:
            return str(next(body.children))

'''
class SoapWsTransferClient(object):

    """SOAP client."""

    def __init__(self, ip_address, port, service, is_secure=False, **kwargs):
        """Set base attributes."""
        self.ip_address = ip_address
        self.port = port
        self.service = service
        self.is_secure = is_secure
        

    @cached_property
    def _session(self):
        """Cached instance of requests.Session."""
        return requests.Session()

    def __call__(self, msg, user="admin", password=""):
        """Post 'msg' to remote service."""
        # generate HTTP request from msg
        url = "http{}://{}:{}/{}".format(
            "s" if self.is_secure else "",
            self.ip_address,
            self.port,
            self.service
            )

        log.debug(url)

        basic_auth = HTTPBasicAuth(user, password)
        # perform HTTP(s) POST
        resp = self._session.post(
            url,
            auth=basic_auth,
            headers={
                "Accept-Encoding":"gzip, deflate",
                "Content-Type":"application/soap+xml; charset=utf-8",
                "Content-Length":str(len(msg)),
                "Expect":"100-continue"
                }, 
            data=msg, 
            verify=False)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        log.debug(resp.content)
        with open(r"c:\result.xml", 'w') as f:
            f.write(resp.content.decode())
        soap_data = BeautifulSoup(resp.content, "xml")
        body = soap_data.find("Body")
        if soap_data.find("Fault"):
            raise SoapFaultException(str(next(body.children)))
        if body is None:
            return ""
        else:
            return str(next(body.children))
'''