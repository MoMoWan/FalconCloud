"""
This is related the LEDM session form requests 
"""
import requests
import requests_usb

class LedmSession(requests.Session):
    """
    This is specific session class for LEDM. It will
    mount the UIO UsbAdapter
    """

    def __init__(self):
        super().__init__()
        self.trust_env = False
        self.mount("uio://", requests_usb.UsbAdapter())

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        """
        override base method to prevent it going to 
        """
        
        return {
            'verify': None, 
            'proxies': {}, 
            'stream': stream, 
            'cert': None}