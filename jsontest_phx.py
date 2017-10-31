import json
import requests

def test_post_ledmset(ip_address="localhost"):
    url = "http://{}:8888/phx/ledm".format(ip_address)
    payload = {"printer": "15.38.201.52",
           "ManufacturingConfigDyn": [
            {"ClearAllCounters":"true"},{"ErrorLogClear":"true"},{"SetupPrompt":"enabled"},{"SerialNumber" : "CN12345678"}
               ],
            "ProductConfigDyn": [{"PowerSaveTimeout": "1minute"}] }
    
    
    headers = {
               'Accept-Language': "en-US",
               #'User-Agent': "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
               #'Content-Type': 'application/json',
               'Accept': "application/json, application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
               "access-control-allow-headers": "content-type",
               "Access-Control-Allow-Origin": "*"
                }
    s = requests.session()
    s.trust_env = False
    r = s.post(url, headers=headers, data=json.dumps(payload))
    return r

def test_get(jobid,ip_address="localhost"):
    url = "http://{}:8888/jedi/nvpconfig?id={}".format(ip_address,jobid)
    headers = {
               'Accept-Language': "en-US",
               #'User-Agent': "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
               #'Content-Type': 'application/json',
               'Accept': "application/json, application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*",
               "access-control-allow-headers": "content-type",
               "Access-Control-Allow-Origin": "*"
                }
    s = requests.session()
    s.trust_env = False
    r = s.get(url,headers=headers, verify=False)
    return r
'''
payload = {"printer": "15.38.201.22",
           "ManufacturingConfigDyn": [
            {"ClearAllCounters":"true"},{"ErrorLogClear":"true"},{"SetupPrompt":"enabled"},{"SerialNumber" : "SN12345678"}
               ],
            "ProductConfigDyn": [{"PowerSaveTimeout": "1minute"}] }
payload =  json.dumps(payload)
jsondata = tornado.escape.json_decode(payload)
jsondata['ManufacturingConfigDyn'][0].keys()
ledm.set_io("15.38.201.52")
ledm.set_http_scheme("HTTP")

timeout = 20
for section in jsondata:
    if section != "printer":
        print ("lemd tree {0}".format(section))
        tree = ledm.create_settable_model(section)
        for node in jsondata[section]:
            for nodename, nodevalue in node.items() :
                tree.set(nodename, nodevalue)
                print("LEDM set {0}  {1}".format(nodename, nodevalue))
        ledm.put(section, tree, timeout)
celery –A tasks_redis worker –-loglevel=debug. 
'''