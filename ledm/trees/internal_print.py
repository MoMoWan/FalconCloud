"""
LEDM wrapper around Internal Print related treee

"""
import logging
log = logging.getLogger(__name__)


from . import ledm_templates
from .ledm_tree import LEDMTree



class InternalPrintDyn(LEDMTree):
    """
    InternalPrintDyn tree /DevMgmt/InternalPrintDyn.xml
    """
    def __init__(self, data=ledm_templates.INTERNAL_PRINT_DYN):
        super().__init__(data)
	
    @property
    def job_type(self):
        """
        Set Internal Print Job Type to initiate
        """
        return self.get("JobType")

    @job_type.setter
    def job_type(self, value):
        self.set("JobType", value)


class InternalPrintCap(LEDMTree):
    """
    InternalPrintCap tree /DevMgmt/InternalPrintCap.xml
    """
    def __init__(self, data):
        super().__init__(data)
	
    @property
    def jobs_supported(self):
        """
        Get a list of supported internal print jobs
        """
        jobs = []
        tjobs = self.get("JobType", True)
        for j in tjobs:
            jobs.append(j.text)
        return jobs