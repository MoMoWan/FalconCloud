"""
manufacturing_proxy.py
"""
__version__ = "$Revision: 47957 $"
__author__  = "$Author: dfernandez $"
__date__    = "$Date: 2016-05-27 14:37:21 -0600 (Fri, 27 May 2016) $ "
 
"""
To Do:

"""

# =============================================================================
# Standard Python modules
# =============================================================================
import sys
import os
import time

# =============================================================================
# logging
# =============================================================================
import logging
log = logging.getLogger("jedilib")

# =============================================================================
# .NET modules
# =============================================================================
import clr
jedi_dll = os.path.join(os.path.dirname(__file__), "HP.Falcon.JediNG.dll")
clr.AddReference(jedi_dll)
from HP.Falcon.JediNG.WebServices.Qualification.IO import RemoteIO

# =============================================================================
# Globals and Definitions
# =============================================================================

