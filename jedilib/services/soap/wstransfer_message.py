import uuid
from .message import SoapMessage
from .message import NS_WSA
from .namespace import NS_WSMAN


class WSTransferSoapMessage(SoapMessage):
    """
    <?xml version="1.0"?>
    <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing">
        <s:Header>
            <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2004/09/transfer/Get</a:Action>
            <h:Locale xmlns:h="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                en-US
            </h:Locale>
            <h:ResourceURI xmlns:h="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
                urn:hp:imaging:con:service:fim:FIMService:ServiceDefaults
            </h:ResourceURI>
            <a:MessageID>
                urn:uuid:df40742c-965f-4c9e-81df-cf50b0ee76eb
            </a:MessageID>
            <a:ReplyTo>
            <a:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
            </a:ReplyTo>
            <a:To s:mustUnderstand="1">http://10.1.1.100:57628/fim</a:To>
        </s:Header>
        <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>
    </s:Envelope>
    
    """

    def __init__(self, action, service, resource, data, ip_endpoint="10.1.100", locale="en-us", is_secure=True):
        """
        action (str): Get, Put
        service (str): the name of the resource like fim
        resource (str): The name of the resource target like urn:hp:imaging:con:service:fim:FIMService:ServiceDefaults
        ip_endpoint (str): The ip address of unit
        is_secure (bool) - True uses port 7627 over HTTPS else use 57628 over HTTP
        """

        actions = ["Get", "Put", "Create", "Delete"] 
        if action not in actions:
            raise ValueError("Unexpected action {} valid actions {}".format(action, actions))
        self.service = service
        self.ip_endpoint = ip_endpoint
        super().__init__(data)

        self.port = 57628
        if is_secure:
            self.port = 7627
        
        self.to = "http://{}:{}/{}".format(ip_endpoint, self.port, service)
        self.action = "http://schemas.xmlsoap.org/ws/2004/09/transfer/{}".format(action)
        self.reply_to = "http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous"

        wsa = self.elementmaker('a', NS_WSA)
        h = self.elementmaker('h', NS_WSMAN)
        message_id = "urn:uuid:" + str(uuid.uuid4())

        nsmap = {
            "h":"http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd",
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsd" :"http://www.w3.org/2001/XMLSchema"
        }
        self.headers = [
             wsa.Action(self.action),
             #h.Locale(locale, namespace="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd", nsmap=nsmap),
             h.Locale(locale),
             #h.ResourceURI(resource, namespace="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd", nsmap=nsmap),
             h.ResourceURI(resource),
             wsa.MessageID(message_id),
             wsa.ReplyTo(wsa.Address(self.reply_to)),
             wsa.To(self.to)
        ]
        
class WSGetTransferSoapMessage(WSTransferSoapMessage):
    def __init__(self, action, service, resource, data, ip_endpoint="10.1.100", locale="en-us", is_secure=True):
        super().__init__("Get", action, service, resource, data, ip_endpoint, locale, is_secure)

class WSPutTransferSoapMessage(WSTransferSoapMessage):
    def __init__(self, action, service, resource, data, ip_endpoint="10.1.100", locale="en-us", is_secure=True):
        super().__init__("Put", action, service, resource, data, ip_endpoint, locale, is_secure)

class WSCreateTransferSoapMessage(WSTransferSoapMessage):
    def __init__(self, action, service, resource, data, ip_endpoint="10.1.100", locale="en-us", is_secure=True):
        super().__init__("Create", action, service, resource, data, ip_endpoint, locale, is_secure)

class WSDeleteTransferSoapMessage(WSTransferSoapMessage):
    def __init__(self, action, service, resource, data, ip_endpoint="10.1.100", locale="en-us", is_secure=True):
        super().__init__("Delete", action, service, resource, data, ip_endpoint, locale, is_secure)