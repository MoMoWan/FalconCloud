"""
Send HTTP Requests over USB
"""

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# Standard Modules
# =============================================================================
from contextlib import contextmanager
import time

# =============================================================================
# 3rd party
# =============================================================================
import win32file
import win32api
import winerror
import win32event
import pywintypes


# =============================================================================
# Globals
# =============================================================================
READ_BUFFER_SIZE = 32768 #32 KB

@contextmanager
def open_http_usb_session(device_path):
    """
    This will open http usb communication session
    """
    http_usb = HttpUsb(device_path)
    http_usb.open()
    yield http_usb
    http_usb.close()

class HttpUsb(object):
    """
    This sends HTTP Requests over USB
    """
    def __init__(self, device_path):
        self.device_path = device_path
        log.debug("Init DevicePath = {}".format(self.device_path))
        self.http_usb_handle = None

    def __enter__(self):
        if self.http_usb_handle == None:
            self.http_usb_handle = self.open()
        return self

    def __exit__(self, *exec):
        self.close()

    def open(self,
        flags_and_attributes=win32file.FILE_FLAG_NO_BUFFERING):
        """
        This will create a handle to usb device
        using the device_path
        Args:

        Returns:
            handle: usb device win32 HANDLE
        """

        http_usb_handle = win32file.CreateFile(
            self.device_path,
            win32file.GENERIC_WRITE|win32file.GENERIC_READ,
            0,
            None,
            win32file.OPEN_EXISTING,
            flags_and_attributes,
            None)
        if http_usb_handle == win32file.INVALID_HANDLE_VALUE:
            error_code = win32api.GetLastError()
            error_message = win32api.FormatMessageW(error_code)
            raise IOError("Open Failed code {} message {}".format(error_code, error_message))
        return http_usb_handle

    def flush(self):
        """
        This wil flush the usb channel. If the
        device handle is None it will try to open
        to flush
        Args:

        Returns:
            bytes: flushed data

        Raises:

        """
        if self.http_usb_handle != None:
            self.close()

        http_usb_handle = self.open(flags_and_attributes=win32file.FILE_FLAG_OVERLAPPED)

        buffer = bytes()
        overlapped = pywintypes.OVERLAPPED()
        overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)
        try:
            while True:
                _, data = win32file.ReadFile(http_usb_handle, READ_BUFFER_SIZE, overlapped)
                rc2 = win32event.WaitForSingleObject(overlapped.hEvent, 60)
                if rc2 == win32event.WAIT_TIMEOUT or rc2 == win32event.WAIT_ABANDONED:
                    break
                elif rc2 == win32event.WAIT_FAILED:
                    log.debug("Error = {}".format(win32.GetLastError()))

                n = win32file.GetOverlappedResult(http_usb_handle, overlapped, False)
                log.debug("n data = {}".format(n))
                if n:
                    buffer += data[:n]
                else:
                    # no data to read
                    break
                win32event.ResetEvent(overlapped.hEvent)
            win32file.CancelIo(http_usb_handle)
        finally:
            win32file.CloseHandle(http_usb_handle)
        self.http_usb_handle = self.open()
        return buffer

    def write_request(self, request):
        """
        This sends the HTTP request over USB device
        HANDLE

        Args:
            request (bytes): Raw HTTP Request

        Returns:
            int: The number of bytes

        Raises:
            IOError: There are couple of scenarios that causes this Exception
                1. all data is not written
                2. write failures
        """
        if isinstance(request, str):
            request = request.encode()
        _, n_bytes_sent = win32file.WriteFile(self.http_usb_handle, request)
        if n_bytes_sent != len(request):
            raise IOError("Write Request did not send entire payload")
        return n_bytes_sent

    def read_request(self):
        """
        This will read raw HTTP response from USB device

        Args:
            usb_scan (handle): usb device handle

        Returns:
            bytes: HTTP Response data
        """
        buffer = bytes()
        max_counter = 100
        current_counter = 0
        while True:
            _, data = win32file.ReadFile(self.http_usb_handle, READ_BUFFER_SIZE)
            if len(data) == 0:
                current_counter += 1
                if current_counter >= max_counter:
                    break
            buffer += data
        return buffer

    def read_headers(self):
        """
        Read HTTP headers. It will
        keep reading lines until \r\n\r\n
        is reached.

        Args:

        Returns:
            bytes: Headers
        """
        max_counter = 100
        current_counter = 0
        headers = bytes()
        while True:
            headers += self.read_line()
            if b"\r\n\r\n" == headers[-4:]:
                break
            current_counter += 1
            if current_counter >= max_counter:
                break
        if len(headers) == 0:
            log.debug("USB NO DATA Wait and Read again")
            time.sleep(1)
            current_counter = 0
            while True:
                headers += self.read_line()
                if b"\r\n\r\n" == headers[-4:]:
                    break
                current_counter += 1
                if current_counter >= max_counter:
                    break
        return headers

    def read_data(self, num_of_bytes):
        """
        Read the number of bytes over USB
        device HANDLE
        """
        log.debug("num_of_bytes = {}".format(num_of_bytes))
        buffer = bytes()
        max_counter = 20
        current_counter = 0
        num_of_data_read = 0
        while True:
            data_to_read = num_of_bytes-num_of_data_read
            log.debug("data_to_read = {}".format(data_to_read))
            rc, data = win32file.ReadFile(self.http_usb_handle, data_to_read)
            log.debug("read_data rc = {} len(data) = {}".format(rc, len(data)))
            if len(data) == 0:
                current_counter += 1
                if current_counter >= max_counter:
                    break
            buffer += data
            num_of_data_read += len(data)
            if num_of_data_read == num_of_bytes:
                break
        return buffer

    def read_line(self):
        """
        This will continue to read until
        \n marker is read to indicate EOL.
        Args:

        Returns:
            bytes: line of HTTP data
        """
        buffer = bytes()
        max_counter = 100
        current_counter = 0
        line = bytes()
        while True:
            rc, data = win32file.ReadFile(self.http_usb_handle, 1)
            #log.debug("read_line rc = {}".format(rc))
            if len(data) == 0:
                current_counter += 1
                if current_counter >= max_counter:
                    break
            line += data
            if data == b'\n':
                break
        return line

    def flush_all_data(self):
        """
        This calls flush multiple times

        Args:

        Returns:
            bytes: The data from flush

        Raises:

        """
        read_loop = 0
        data = bytes()
        while True:
            tempData = self.flush()
            if read_loop > 5:
                break
            if len(tempData) == 0:
                time.sleep(.2)
                read_loop += 1
            else:
                read_loop = 0
            data += tempData
        return data

    def send_http_request(self, request):
        """
        Sends raw HTTP request and returns raw HTTP response

        Args:
            request (bytes): raw HTTP request

        Returns:
            (bytes): HTTP response
        """
        if self.http_usb_handle == None:
            self.http_usb_handle = self.open(flags_and_attributes=win32file.FILE_FLAG_OVERLAPPED)
        data = bytes()
        try:
            self.write_request(request)
            time.sleep(.1)
            data = self.read_request()
        finally:
            self.close()
        return data

    def close(self):
        """
        This will close the USB HTTP HANDLE
        """
        log.debug("Close Handle")
        win32file.CloseHandle(self.http_usb_handle)