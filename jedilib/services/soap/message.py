"""
The creation of the SOAP Messages is based off ideas from
https://github.com/tysonclugg/rinse

"""

import uuid
import lxml
from lxml import etree
from lxml.builder import ElementMaker
import requests
from .namespace import NS_BODY, NS_SOAPENV, NS_WSA


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
    """
    SOAP message.
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

    def elementmaker(self, prefix, url):
        """
        Register namespace and return ElementMaker bound to the namespace.
        """
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
        """
        Generate a SOAP Envelope message with header and body elements.
        """
        
        soapenv = self.elementmaker('s', NS_SOAPENV)
        nsmap = {
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsd" :"http://www.w3.org/2001/XMLSchema"
        }
        msg = soapenv.Envelope(
            soapenv.Header(*self.headers),
            soapenv.Body(self.body, nsmap)
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