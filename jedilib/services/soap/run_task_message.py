"""
This is specific to Run Task Soap Message
"""
import uuid
import html
import lxml
from lxml import etree
from lxml.builder import ElementMaker
import requests

from .message import SoapMessage
from .namespace import NS_WSA


class RunTaskSoapMessage(SoapMessage):
    """
    <?xml version="1.0"?>
    <s:Envelope xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:s="http://www.w3.org/2003/05/soap-envelope">
        <s:Header>
            <a:MessageID>urn:uuid:ee7da3bb-eb3f-4f00-8a95-48a3ffa9f03a</a:MessageID>
            <a:To>http://10.1.1.100:65102/remoteinvocation</a:To>
            <a:Action>http://www.hp.com/schemas/imaging/con/service/qualification/controlpanel/2009/10/26/RunTask</a:Action>
            <a:ReplyTo>
            <a:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
            </a:ReplyTo>
        </s:Header>
        <Body xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26">
            <taskName>RisDeviceTask</taskName>
            <methodIdentifier>geterrorlogentries</methodIdentifier>
            </RunTask>
        </Body>
    </s:Envelope>    
    """

    def __init__(self, task_name, method, param=None, ip_endpoint="10.1.100", service="remoteuserinterface"):
        """
        service = remoteuserinterface (23) or controlpanel (24)
        """

        tbody = '<RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26"><taskName>{}</taskName><methodIdentifier>{}</methodIdentifier></RunTask>'.format(task_name, method)                
        if param is not None:
            param_msg = ""
            for p in param:
                param_msg += "<parameters>{}</parameters>".format(html.escape(p))
            tbody = '<RunTask xmlns="http://www.hp.com/schemas/imaging/con/service/qualification/remoteinvocation/2009/10/26"><taskName>{}</taskName><methodIdentifier>{}</methodIdentifier>{}</RunTask>'.format(task_name, method, param_msg)

        super().__init__("BODY")

        self.service = service
        self.ip_endpoint = ip_endpoint
        self.tbody = tbody.strip()
        self.to = "http://{}:65102/remoteinvocation".format(ip_endpoint)
        self.action = "http://www.hp.com/schemas/imaging/con/service/qualification/{}/2009/10/26/RunTask".format(service)
        self.reply_to = "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"

        wsa = self.elementmaker('a', NS_WSA)
        message_id = "urn:uuid:" + str(uuid.uuid4())
        
        self.headers = [
            wsa.Action(self.action),
            wsa.MessageID(message_id),
            wsa.ReplyTo(wsa.Address(self.reply_to)),
            wsa.To(self.to)
            ]
        
    def tostring(self, **kwargs):
        msg = super().tostring(encoding='unicode', **kwargs)
        msg = msg.replace("BODY",self.tbody)
        return msg

    def __str__(self):
        """Generate XML (unicode)."""
        return self.tostring(encoding='unicode')
        
