import logging
import json
import tornado.escape
from tornado.web import RequestHandler
from tasks_redis import send_fim_bundle_task

class MfgBundleHandler(RequestHandler):
    """
    This will handle nvp set services. It will provide a service
    to create task and get task status
    """

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        """
        HTTP GET /jedi/fimbundle?id={}
        """
        task_id = self.get_argument('id')
        task = send_fim_bundle_task.AsyncResult(task_id)
        logging.info("task_id==  %r ", task_id)
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
            #if 'result' in task.info:
             #   response['result'] = task.info['result']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                #'status': str(task.info),  # this is the exception raised
                'traceback': task.traceback # The traceback if the task failed.
            }
        self.write(json.dumps(task.state))

    def post(self):
        """
        This will initiate sending fim bundle to printer
        """
        jsondata = tornado.escape.json_decode(self.request.body)
        logging.info("json ==  %r ", jsondata)

        printer = jsondata['printer']
        bundle_file_path = jsondata['bundle_file_path']
        user_name = jsondata.get('username',"admin")
        password = jsondata.get('password', "")

        task = send_fim_bundle_task.delay(printer,bundle_file_path,user_name,password)
        response = {
                'state': task.state,
                'id': task.id
            }
        self.write(json.dumps(response))