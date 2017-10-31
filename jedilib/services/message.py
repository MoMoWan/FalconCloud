"""SOAP client."""
from __future__ import print_function
import uuid
import lxml
from lxml import etree
from lxml.builder import ElementMaker
import requests


NS_SOAPENV = 'http://www.w3.org/2003/05/soap-envelope'
NS_WSA = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
NS_BODY = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'

class ElementMaker(ElementMaker):
    """Wrapper around lxml ElementMaker that casts ints as strings."""

    def __getattr__(self, name):
        """Return a lambda that parses int args as strings."""
        _cls = super(ElementMaker, self).__getattr__(name)

        def __cls_wraper(*args, **kwargs):
            """Wrapper around Element class."""
            return _cls(
                *[
                    str(arg) if isinstance(arg, int) else arg
                    for arg
                    in args
                ],
                **kwargs
            )
        return __cls_wraper



class SoapMessage:

    """SOAP message.

    >>> from rinse.message import SoapMessage
    >>> from lxml import etree
    >>> from rinse.util import printxml
    >>> body = etree.Element('test')
    >>> msg = SoapMessage(body)
    >>> printxml(msg.etree())
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
      <soapenv:Header/>
      <soapenv:Body>
        <test/>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    elementmaker_cls = ElementMaker

    def __init__(self, body=None):
        """Set base attributes."""
        # XML namespace map
        self._nsmap = {}
        # cache of lxml.etree.ElementMaker instances by namespace prefix
        self._elementmaker_cache = {}
        # SOAP headers
        self.headers = []
        # SOAP body
        self.body = body

        self.to = ""
        self.action = ""
        self.reply_to = ""

        # HTTP headers
        self.http_headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
        }

    def __getitem__(self, key):
        """Dict style access to http_headers."""
        return self.http_headers[key]

    def __setitem__(self, key, val):
        """Dict style access to http_headers."""
        self.http_headers[key] = val

    def __delitem__(self, key):
        """Dict style access to http_headers."""
        del self.http_headers[key]

    def elementmaker(self, prefix, url):
        """Register namespace and return ElementMaker bound to the namespace."""
        try:
            old_url = self._nsmap[prefix]
            if url != old_url:
                raise ValueError(
                    'Namespace {!r} already defined as {!r}.'.format(
                        prefix,
                        old_url,
                    ),
                )
        except KeyError:
            self._nsmap[prefix] = url
            self._elementmaker_cache[prefix] = self.elementmaker_cls(
                namespace=url, nsmap=self._nsmap,
            )
        return self._elementmaker_cache[prefix]

    def etree(self):
        """Generate a SOAP Envelope message with header and body elements."""
        

        wsa = self.elementmaker('a', NS_WSA)
        message_id = "urn:uuid:" + str(uuid.uuid4())
        """
        to = "http://10.1.1.100:65102/remoteinvocation"
        action = "http://www.hp.com/schemas/imaging/con/service/qualification/{}/2009/10/26/RunTask"
        reply_to = "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"
        wsa.MessageID(message_id)
        

        self.headers.extend(
            header
            for header in [
                wsa.MessageID(message_id),
                wsa.To(self.to),
                wsa.Action(self.action),
                wsa.ReplyTo(wsa.Address(self.reply_to)),
            ]
        )
        """

        wsa_headers = [
                wsa.MessageID(message_id),
                wsa.To(self.to),
                wsa.Action(self.action),
                wsa.ReplyTo(wsa.Address(self.reply_to)),
            ]
        headers = self.headers + wsa_headers

        soapenv = self.elementmaker('s', NS_SOAPENV)
        nsmap = {
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsd" :"http://www.w3.org/2001/XMLSchema"
        }
        body = ElementMaker(nsmap=nsmap)
        msg = soapenv.Envelope(
            soapenv.Header(*headers),
            soapenv.Body("BODY", nsmap)
        )
        
        return msg

    def tostring(self, **kwargs):
        """Generate XML representation of self."""
        return etree.tostring(self.etree(), **kwargs)

    def request(self, url=None, action=None):
        """Generate a requests.Request instance."""
        headers = self.http_headers.copy()
        if action is not None:
            headers['SOAPAction'] = action
        return requests.Request(
            'POST',
            url or self.url,
            data=self.tostring(pretty_print=True, encoding='utf-8'),
            headers=headers,
        )

    def __bytes__(self):
        """Generate XML (bytes)."""
        return self.tostring()

    def __str__(self):
        """Generate XML (unicode)."""
        return self.tostring(encoding='unicode')

class RisSoapMessage(SoapMessage):
    """
    <RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26">
      <taskName>RisDeviceTask</taskName>
      <methodIdentifier>nvramsetbatch</methodIdentifier>
      <parameters>{}</parameters>
    </RunTask>
    """

    def __init__(self, task_name, method, param=None, uut_ip_endpoint="10.1.100", service="remoteuserinterface"):
        """
        service = remoteuserinterface (23) or controlpanel (24)
        """

        tbody = '<RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26"><taskName>{}</taskName><methodIdentifier>{}</methodIdentifier></RunTask>'.format(task_name, method)                
        if param is not None:
            param_msg = ""
            for p in param:
                param_msg += "<parameters>{}</parameters>".format(p)
            tbody = '<RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26"><taskName>{}</taskName><methodIdentifier>{}</methodIdentifier><parameters>{}</parameters></RunTask>'.format(task_name, method, param_msg)

        self.tbody = tbody.strip()
        super().__init__("BODY")

        self.uut_ip_endpoint = uut_ip_endpoint
        self.to = "http://{}:65102/remoteinvocation".format(uut_ip_endpoint)
        self.action = "http://www.hp.com/schemas/imaging/con/service/qualification/{}/2009/10/26/RunTask".format(service)
        self.reply_to = "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"

    def tostring(self, **kwargs):
        msg = super().tostring(encoding='unicode')
        msg = msg.replace("BODY",self.tbody)
        return msg

    def __bytes__(self):
        """Generate XML (bytes)."""
        return self.tostring()

    def __str__(self):
        """Generate XML (unicode)."""
        return self.tostring(encoding='unicode')
        
