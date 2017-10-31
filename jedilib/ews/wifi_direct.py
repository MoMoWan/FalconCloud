"""
wifi_direct.py

"""
__version__ = '$Revision: 48177 $'
__author__  = '$Author: dfernandez $'
__date__    = '$Date: 2016-06-20 08:18:39 -0600 (Mon, 20 Jun 2016) $'

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import time
import socket
import functools

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger(__name__)

# =============================================================================
# 3rd Party modules
# =============================================================================
import requests
from bs4 import BeautifulSoup


class WifiDirect(object):
    '''
    Wifi Direct EWS web scrapes values from HTML provided by the EWS server. 
    '''
    def __init__(self):
        self.ConnectedClients = None
        self.WirelessDirectPrinting = None
        self.IPAddress = None
        self.Channel = None
        self.AllowBroadcast = None
        self.SSID = None
        self.ConnectionMethod = None
        self.WDPassPhrase = None

class WifiDirectCreator:
    @staticmethod
    def CreateWifiDirect(soup):
        '''
        Creator of an WifiDirect object from a soup stream.
        Expected soup from an EWS page Wireless Direct Setup.
        Each static method is for an element on the ews page.
        '''
        wifiDirect = WifiDirect()
        wifiDirect.ConnectedClients = WifiDirectCreator._GetConnectedClients(soup)
        wifiDirect.WirelessDirectPrinting = WifiDirectCreator._GetWirelessDirectPrinting(soup)
        wifiDirect.IPAddress = WifiDirectCreator._GetIPAddress(soup)
        wifiDirect.Channel = WifiDirectCreator._GetChannel(soup)
        wifiDirect.AllowBroadcast = WifiDirectCreator._IsBroadcast(soup)
        wifiDirect.SSID = WifiDirectCreator._GetSSID(soup)
        wifiDirect.ConnectionMethod = WifiDirectCreator._GetConnectionMethod(soup)
        wifiDirect.WDPassPhrase = WifiDirectCreator._GetWdPassPhrase(soup)
        return wifiDirect
       
    @staticmethod  
    def _GetSSID(soup):
        ''' returns SSID is from the wifi card in the printer '''
        t = soup.findAll(lambda tag: tag.name == "div" and tag.has_attr('id') and tag["id"] == "div2")
        if len(t) != 1:
            raise Exception("Error EWS Wireless Direct Setup Page -> SSID Missing")
        prefix = t[0].text
        log.debug("Printer Wifi SSID = " + prefix + " " + t[0].find('input')["value"])
        return prefix + " " + t[0].find('input')["value"]

    @staticmethod
    def _IsBroadcast(soup):
        ''' 
        returns bool of the check box for Allow Broadcast of Name(SSID) 
        true if checked and false if not
        '''
        try:
            t = soup.findAll(lambda tag: tag.name == "input" and  tag.has_attr('id') and tag["id"] == "wd_broadcast")
            if len(t) != 1:
                raise Exception("Error EWS Wireless Direct Setup Page -> Allow Broadcast of SSID Name Missing")
            log.debug("Allow Broadcast of Name(SSID) -> " + str("checked" in t[0])) 
        except:
            log.debug("Broadcast field not found")
            return False
        return "checked" in t[0]
        
    @staticmethod
    def _GetChannel(soup):
        ''' returns the printer wifi access point channel being used '''
        t = soup.findAll(lambda tag: tag.name == "option" and  tag.has_attr('value') and  tag.has_attr('selected'))
        for selected in t:
            value = selected.text.strip()
            if value.isdigit():
                log.debug("Printer wifi access point channel = " + value )
                return value
                
        raise Exception("Error EWS Wireless Direct Setup Page -> Channel Missing")
        
    @staticmethod
    def _GetConnectionMethod(soup):
        ''' returns the printer wifi access point channel being used '''
        t = soup.findAll(lambda tag: tag.name == "select" and  tag.has_attr('id') and tag["id"] == "ConnMethod")
        if len(t) != 1:
            return "None"
        select = t[0]
        t = select.findAll(lambda tag: tag.has_attr('selected'))
        if len(t) != 1:
            raise Exception("Error EWS Wireless Direct Setup Page -> Could not determine Connection Method")
        log.debug("Connection Method = " + t[0].text)
        return t[0].text
        
    @staticmethod
    def _GetWdPassPhrase(soup):
        ''' returns the printer wifi access point channel being used '''
        t = soup.findAll(lambda tag: tag.name == "input" and tag.has_attr('id') and "wd_PassPhrase" in tag["id"])
        if len(t) != 1:
            return ""
        value = t[0]['value']
        log.debug("WD PassPhrase = " + value)
        return value
        
    @staticmethod    
    def _GetIPAddress(soup):
        ''' returns ip address of the printer wifi access point '''
        t = soup.findAll(lambda tag: tag.name == "div" and tag.has_attr('id') and "div10" in tag["id"])
        if len(t) != 1:
            raise Exception("Error EWS Wireless Direct Setup Page -> IP Address Missing")
        log.debug("Ip Address of the printer wifi access point = " + t[0].text)
        return t[0].text
    @staticmethod
    def _GetWirelessDirectPrinting(soup):
        ''' returns the enable (on no security) or (on with security) or disabled {off) '''
        t = soup.findAll(lambda tag: tag.name == "select" and tag.has_attr('id') and "WDPrinting" in tag["id"])
        if len(t) != 1:
            raise Exception("Error EWS Wireless Direct Setup Page -> Wireless Direct Printing Missing")
            
        select = t[0]
        t = select.findAll(lambda tag:  tag.has_attr('selected'))
        if len(t) != 1:
            raise Exception("Error EWS Wireless Direct Setup Page -> Wireless Direct Printing Selection Missing")
        log.debug("The printer Wireless Direct Printing state = " + t[0].text)
        return t[0].text
        
    @staticmethod
    def _GetConnectedClients(soup):
        ''' 
        returns the elements of the Connected Clients table as ConnectedClients(object)
        with Mac address and ip address of each client connected. Normally this would be one client falcon test station
        ''' 
        t = soup.findAll(lambda tag: tag.name == "table" and tag.has_attr('class') and tag["class"] == "dataTable")
        if len(t) == 0:
            # if the reg pattern is 0 or no table found then try new omni ews page has different search pattern
            t = soup.findAll(lambda tag: tag.name == "div" and tag.has_attr('class') and tag["class"] == " dataTable ")
            return []
        '''    
        elif len(t) != 1:
            raise Exception(str.format("Error EWS Wireless Direct Setup Page -> unexpected number {0} of Connected Clients tables",len(t)))
        '''    
        table = t[0]
        headers = table.findAll('th')
        rows = table.findAll('tr')
        elements = []
        for row in rows:
            cells = row.findAll('td')
            if len(cells) != 3:
                continue
            elements.append(ConnectedClients(cells[1].text.replace("&nbsp;","").replace(":","").upper(),cells[2].text.replace("&nbsp;","")))
            log.debug(str.format("Connected client {0} : {1}", elements[-1].MacAddress, elements[-1].IPAddress))
        log.debug(str.format("Found {0} connected clients", len(elements)))    
        return elements