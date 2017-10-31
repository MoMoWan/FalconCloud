import logging
log = logging.getLogger(__name__)

import re
import lxml.etree as et
from bs4 import BeautifulSoup
from collections import namedtuple
from . import ledm_templates


_XSLT_REMOVE_EMPTY_TAGS = """<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output omit-xml-declaration="yes" indent="yes"/>
 <xsl:strip-space elements="*"/>
 <xsl:template match="node()|@*">
        <xsl:if test="normalize-space(string(.)) != ''">
                <xsl:copy>
                        <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
        </xsl:if>
 </xsl:template>
 <xsl:template match=
    "*[not(@*|*|comment()|processing-instruction()) 
     and normalize-space()=''
      ]"/>
</xsl:stylesheet>"""


XSLT_REMOVE_TAGES = et.fromstring(_XSLT_REMOVE_EMPTY_TAGS)

class LEDMTree(object):
    """
    Base class for LEDM Trees contains 
    basic features for writing/reading nodes
    """

    def __init__(self, data):
        #self.__dict__['data'] = BeautifulSoup(data, "xml")
        self.data = BeautifulSoup(data, "xml")

    def __str__(self):
        transform = et.XSLT(XSLT_REMOVE_TAGES)
        temp_data = et.fromstring(self.data.encode('UTF-8'))
        newdom = transform(temp_data)
        return et.tostring(newdom, encoding='UTF-8', xml_declaration=True).decode('UTF-8')
     
    def get(self, node_name, aslist=False):
        """
        Get Node from data
        """
        offset = 0
        if re.search("\[", node_name):
            node_name, tmpstr = node_name.split("[")
            offset = int(tmpstr.split("]")[0])
        rtnData = self.data.findAll(node_name)
        if aslist:
            return rtnData
        else:
            if len(rtnData) == 0:
                return ""
            return rtnData[offset].text

    def set(self, node_name, value):
        offset = 0
        if re.search("\[", node_name):
            node_name, tmpstr = node_name.split("[")
            offset = int(tmpstr.split("]")[0])
        rtnData = self.data.findAll(node_name)        
        rtnData[offset].string = value
