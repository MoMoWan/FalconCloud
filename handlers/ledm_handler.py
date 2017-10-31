import logging
import json
import tornado.escape
from tornado.web import RequestHandler
from tasks_redis import nvp_sets
from tasks_redis import ledm_set
import subprocess
import platform

def ping(ip,retries=1,timeout = 10):
    while (retries!=0):
        ping_command = ['ping', ip, '-w', str(timeout)]
        shell_needed = True
        ping_output = subprocess.run(ping_command,shell=shell_needed,stdout=subprocess.PIPE)
        success = ping_output.returncode
        retries = retries - 1
    return True 
    #return True if success == 0 else False
	
class LedmHandler(tornado.web.RequestHandler):
    """
    This will handle LEDM set services. It will provide a service
    to create task and get task status
    """

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        """
        HTTP GET /jedi/nvpconfig?id={}
        """
        task_id = self.get_argument('id')
        task = nvp_sets.AsyncResult(task_id)
        response = {
            'state': "Unknown",
            'status': 'Pending...'
        }
        if task.state == 'PENDING':
            #// job did not start yet
            response = {
                'state': task.state,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'status': task.status
            }
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                #'status': str(task.info),  # this is the exception raised
                'status': task.traceback # The traceback if the task failed.
            }
        logging.info("task_id ==  {} state = {} status = {}".format(task_id, response['state'], response['status']))
        self.write(json.dumps(response))

    def post(self):

        jsondata = tornado.escape.json_decode(self.request.body)
        logging.info("json ==  %r ", jsondata)
        printer = jsondata['printer']
        # we will use the task id to query task status
        if ping (str(printer)):
            task = ledm_set.delay(printer,jsondata)
            # we will use the task id to query task status
            response = {
                'state': task.state,
                'id': task.id
            }
            self.write(json.dumps(response))
        else:
            self.write (printer + ' is not reachable.')