"""
This handles internal print jobs
"""

import logging
log = logging.getLogger(__name__)

import time
from enum import Enum
from . import ledm_api
from .trees import ledm_templates
from .trees import ledm_tree
from . import trees
from . import resource



def initiate(job_name):
    """
    This will initiate internal job based on the job name. Examples of 
    job_name are:
        faxAllFaxReports
        faxActivityLog
        faxConfirmationReport
        faxErrorReport
        faxJunkFaxListReport
        faxLastCallReport
        faxPhoneBookReport
        faxBillingCodesReport
        demoPage
        suppliesStatusPage
        usagePage
        networkSummary
        wirelessNetworkPage
        cleaningPage
        servicePage
        configurationPage
        quickFormNotebookNarrowRule
        quickFormNotebookWideRule
        quickFormNotebookChildRule
        quickFormGraphEighthInch
        quickFormGraph5mm
        quickFormChecklist1Column
        quickFormChecklist2Column
        quickFormMusicPortrait
        quickFormMusicLandscape

    Args:
        job_name (str): The internal job name

    Returns:
        dict: HTTP headers

    """
    internal_job = trees.InternalPrintDyn()
    internal_job.job_type = job_name
    return ledm_api.post(resource.InternalPrintDyn,internal_job)
    