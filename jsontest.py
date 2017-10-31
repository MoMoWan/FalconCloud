import json
import requests

def test_post(ip_address="localhost"):
    url = "http://{}:8888/jedi/nvpconfig".format(ip_address)
    payload = {"printer": "15.86.231.12",
           "nvps": [
               [
                   "845E3285-C67C-4F4B-9AA4-0AE91BD35089",
                   "JDIMfgReset",
                   "hex",
                   "01000000"
               ],
               [
                   "1429e79e-d9ba-412e-a2bc-1f3d245041ce",
                   "SerialNumber",
                   "str",
                   "SH1234567"
               ]
           ],
           "username": "admin",
           "password": "!QAZ2wsx"
           }
    
    
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