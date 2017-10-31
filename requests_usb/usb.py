"""
request usb adapters
"""
import logging
import time
import base64
import requests

from requests import Response
from requests.compat import urlparse
from requests.utils import get_encoding_from_headers
import pywintypes

import usb_device
from . import http_usb


log = logging.getLogger(__name__)

PRINTER = None

def build_response(request, data, code, reason, headers={}, encoding=None):
    """Builds a response object from the data"""
    response = Response()
    response.status_code = code

    for k, v in headers.items():
        response.headers[k] = v
    response.encoding = encoding
    if not encoding:
        response.encoding = get_encoding_from_headers(response.headers)
    response.raw = data
    response._content = data
    response.url = request.url
    response.request = request
    response.reason = reason

    return response

class UsbSession(requests.Session):
    """
    Inherits from requests.Session for using
    for USB Communication
    """

    def __init__(self):
        self.trust_env = False
        super().__init__()
        self.mount("uio://", UsbAdapter())

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        """
        override base method to prevent it going to
        """
        return {'verify': None, 'proxies': {}, 'stream': stream, 'cert': None}


class NoPrinterDectedException(Exception):
    """Exception for No Printers Detected"""
    pass

class MultiplePrintersDetectedException(Exception):
    """Exception for Multiple Exception"""
    pass

class UsbAdapter(requests.adapters.BaseAdapter):
    """A Requests Transport Adapter that handles USB urls."""

    def __init__(self):
        super().__init__()
        self.printer = None

    def get_printer(self, port_name=""):
        """
        Retreive printer object
        """

        global PRINTER
        if PRINTER is not None:
            return PRINTER

        printers = []
        try:
            printers = usb_device.get_printers()
        except AttributeError as ex:
            log.debug("usb_device.get_printers() Attribute error {}".format(ex))

        num_of_printers = len(printers)
        if num_of_printers == 0:
            raise NoPrinterDectedException()
        elif num_of_printers > 1:
            raise MultiplePrintersDetectedException()

        PRINTER = printers[0]
        return PRINTER


    def send(self, request, **kwargs):
        """
        Sends a PreparedRequest object over HTTP. Returns a response object.
        """
        global PRINTER
        if self.printer is None:
            self.printer = self.get_printer()
        try:
            return self._send(request, **kwargs)
        except pywintypes.error as ex:
            PRINTER = None
            self.printer = None
            self.printer = self.get_printer()
            if self.printer is None:
                log.exception(str)
                raise IOError("USB Communicaton Lost")
            # try one more time
            try:
                return self._send(request, **kwargs)
            except pywintypes.error as ex:
                PRINTER = None
                self.printer = None
                log.exception(str)
                raise IOError("USB Communication Lost")
        except Exception as ex:
            PRINTER = None
            self.printer = None
            return build_response(
                request,
                str(ex).encode(),
                503,
                str(ex).encode(),
                headers={},
                encoding='utf-8')


    def _send(self, request, **kwargs):
        """
        This will send the write/read HTTP request
        """

         # Next, get the host and the path.
        _, _, path = self.get_host_and_path_from_url(request)

        # Prepare Raw Request
        raw_request = self.create_raw_request(request, path)
        log.warning("request\n{}".format(raw_request))

        temp_value = kwargs.get("timeout", .15)
        if temp_value is None:
            temp_value = 0.15
        time_to_sleep = float(temp_value)
        log.debug("time_to_sleep = {}".format(time_to_sleep))
        # Send Request and Read Raw Data
        with http_usb.HttpUsb(self.printer.http_device_path) as usb_device:
            log.debug("Flush")
            usb_device.flush()
            log.debug("write request")
            usb_device.write_request(raw_request)
            time.sleep(time_to_sleep)
            log.debug("read request headers")
            raw_headers = usb_device.read_headers()
            status_line, headers, status_code, reason = self.parse_for_status_line_and_headers(raw_headers)
            log.debug(status_line)
            log.debug(headers)
            body = bytes()
            if request.method == 'HEAD':
                #HEAD action have no body
                pass
            elif "CONTENT-LENGTH" in headers:
                content_length = int(headers["CONTENT-LENGTH"])
                if content_length == 0:
                    body = b""
                else:
                    body = usb_device.read_data(content_length)
            else:
                #chunked data
                log.debug("CHUNKED DATA")
                while True:
                    chunk_size = int(usb_device.read_line(), 16)
                    log.debug("chunk_size = {}".format(chunk_size))
                    if chunk_size == 0:
                        break
                    body += usb_device.read_data(chunk_size)
                    usb_device.read_data(2) # remove /r/n
            log.debug(body)
            resp = build_response(request, body, status_code, reason, headers)
            return resp

    def parse_for_status_line_and_headers(self, raw_response_data):
        """
        This will parse for the status line and HTTP headers

        Args:
            bytes: HTTP Data

        Returns:
            (str, {str:str}, int, str):status_line, headers, code, reason
        """
        if len(raw_response_data) == 0:
            return 510, "NO Data Available", {}, "NO Data Available"
        else:
            temp_data = raw_response_data
            if isinstance(raw_response_data, bytes):
                temp_data = raw_response_data.decode('utf-8')
            end_of_header = temp_data.find("\r\n\r\n")
            import email
            import io
            status_line, headers_alone = temp_data[:end_of_header].split("\r\n", 1)
            message = email.message_from_file(io.StringIO(headers_alone))
            temp_headers = dict(message.items())
            headers = {}
            for k,v in temp_headers.items():
                headers[k.upper()] = v
            code = status_line.split(" ")[1]
            if code.isdigit():
                code = int(code)
            else:
                code = 200
            reason = status_line.split(" ")[2]
            return status_line, headers, code, reason

    def parse_raw_response(self, raw_response_data):
        """
        Parses raw HTTP data and create status code, headers, and
        body

        Args:
            raw_response_data (bytes): the raw HTTP response byte code

        Return:
            (int,str, {str:str},bytes): returns status code, reason, headers, and body
        """
        if len(raw_response_data) == 0:
            return 510, "NO Data Available", {}, "NO Data Available"
        else:
            temp_data = raw_response_data
            if isinstance(raw_response_data, bytes):
                temp_data = raw_response_data.decode('utf-8')
            end_of_header = temp_data.find("\r\n\r\n")
            import email
            import io
            request_line, headers_alone = temp_data[:end_of_header].split("\r\n", 1)
            message = email.message_from_file(io.StringIO(headers_alone))
            headers = dict(message.items())
            body = temp_data[end_of_header:].strip()
            code = request_line.split(" ")[1]
            if code.isdigit():
                code = int(code)
            else:
                code = 200
            reason = request_line.split(" ")[2]

            return code, reason, headers, body.encode()

    def create_raw_request(self, request, path):
        """
        This will take a request object and create a raw request format

        Args:
            request (PrepareRequest): object that comes from request library

        Returns:
            str: raw request
        """

        if not path.startswith("/"):
            path = "/" + path
        request_line = "{} {} HTTP/1.1".format(request.method, path)
        request.headers["HOST"] = "USB"
        if "Connection" in request.headers:
            del request.headers["Connection"]

        if "Accept-Encoding" in request.headers:
            del request.headers["Accept-Encoding"]

        headers = "\r\n".join(["{}: {}".format(k, v) for k, v in request.headers.items()]) + "\r\n"
        data = ""
        if request.body:
            data = request.body

        raw_request = "{}\r\n{}\r\n{}".format(
            request_line,
            headers,
            data)

        #log.debug("raw_request\n{}".format(raw_request))
        return raw_request


    def get_username_password_from_header(self, request):
        """Given a PreparedRequest object, reverse the process of adding HTTP
        Basic auth to obtain the username and password. Allows the FTP adapter
        to piggyback on the basic auth notation without changing the control
        flow."""
        auth_header = request.headers.get('Authorization')

        if auth_header:
            # The basic auth header is of the form 'Basic xyz'. We want the
            # second part. Check that we have the right kind of auth
            # though.
            encoded_components = auth_header.split()[:2]
            if encoded_components[0] != 'Basic':
                raise AuthError('Invalid form of Authentication used.')
            else:
                encoded = encoded_components[1]

            # Decode the base64 encoded string.
            decoded = base64.b64decode(encoded)

            # The string is of the form 'username:password'. Split on the
            # colon.
            components = decoded.split(':')
            username = components[0]
            password = components[1]
            return (username, password)
        else:
            # No auth header. Return None.
            return None

    def get_host_and_path_from_url(self, request):
        """Given a PreparedRequest object, split the URL in such a manner as to
        determine the host and the path. This is a separate method to wrap some
        of urlparse's craziness."""
        url = request.url
        
        # scheme, netloc, path, params, query, fragment = urlparse(url)
        parsed = urlparse(url)
        path = parsed.path
        print("parsed = {}".format(parsed))
        # If there is a slash on the front of the path, chuck it.
        if len(path) > 0 and path[0] == '/':
            path = path[1:]
        query = parsed.query
        if query:
            path = "{}?{}".format(path, query)
        host = parsed.hostname
        port = parsed.port or 0

        return (host, port, path)

    def close(self):
        """Dispose of any internal state."""
        # Currently this is a no-op.
        pass

class AuthError(Exception):
    """Denotes an error with authentication."""
    pass