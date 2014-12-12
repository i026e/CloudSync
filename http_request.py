#encoding:UTF-8
import http.client as httplib

class request():
    headers = {}
    url = ''
    all_headers = {'Accept': '*/*',
        'Authorization': '',
        'Expect': '100-continue',
        'Content-Type': 'application/binary',
        'Depth': 1,
        'Content-Length': 0}
    header_types = {'folder_status': ('Accept',
                                      'Authorization',
                                      'Depth'),
                    'common': ('Accept',
                                      'Authorization'),
                    'download': ('Accept',
                                  'Authorization',
                                  'Content-Type'),
                    'upload': ('Accept',
                                  'Authorization',
                                  'Expect',
                                  'Content-Type',
                                  'Content-Length')}
    def __init__(self, url, auth_header=''):
        self.url = url
        self.all_headers['Authorization'] = auth_header


    # set headers
    def set_headers(self, header_type, content_len=None):
        self.headers = {}
        for key, val in self.all_headers.items():
            if key in self.header_types[header_type]:
                self.headers[key] = val
        if content_len:
            self.headers['Content-Length'] = content_len

    # send request
    def send_request(self, method, path, data=None):
        conn = httplib.HTTPSConnection(self.url)
        conn.putrequest(method, path)
        for key, value in self.headers.items():
            conn.putheader(key, value)
        conn.endheaders()
        if data:
            conn.send(data)
        response = conn.getresponse()
        status = response.status
        data = response.read()
        headers = response.getheaders()
        conn.close()
        return {'status':status, 'data':data, 'headers':headers }