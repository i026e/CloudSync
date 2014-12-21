#encoding:UTF-8
from urllib.parse import quote, unquote
import dateutil.parser
import http.client as httplib
import json
from uuid import uuid4


def find_index(list_l, elem):
    try:
        return list_l.index(elem)
    except ValueError as e:
        return None

# decode strings like %D0%A4%D0%BE%D1%82%D0%BE
def url_decode(string):
    return unquote(string)
# encode strings
def url_encode(string):
    return quote(string)#, safe='')

def get_json_from_file(filename):
    with open(filename,'r') as f:
        s = f.read()
        return json.loads(s, encoding='utf-8')

def rand_str():
    return str(uuid4())

# split path to folders and filename by last /
def split_filepath(filepath):
    last_slash_ind = filepath.rfind('/')
    folders = ''
    if last_slash_ind > 0:
        folders = filepath[:last_slash_ind]
    return folders, filepath[last_slash_ind+1:]

class http_request():
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


class File():
    DIRECTORY_MTYPE = "directory"
    def __init__(self, id, name, mtype, size, mtime, ctime):
        self.id = id
        self.name = name.strip('/')
        self.mtype = mtype
        self.size = self._conv2_int_(size)
        self.mtime = self._conv2_date_time_(mtime)
        self.ctime = self._conv2_date_time_(ctime)

    def _conv2_date_time_(self, str_date):
        try:
            return dateutil.parser.parse(str_date)
        except ValueError as e:
            print(e)
            return None
    def _conv2_int_(self, str_int):
        try:
            return int(str_int)
        except ValueError as e:
            print(e)
            return -1

    def is_dir(self):
        return self.mtype == self.DIRECTORY_MTYPE

    def is_bigger_than(self, other):
        return self.size > other.size

    def is_newer_than(self, other):
        try:
            return self.mtime > other.mtime
        except TypeError as e:
            print(e)
            return False


class conflict_resolver():
    SKIP = 0
    REPLACE = 1
    KEEP_LARGEST = 2
    KEEP_NEWEST = 3

    def __init__(self, method):
        #associate methods with functions
        options = {
            self.SKIP : self.skip,
            self.REPLACE : self.replace,
            self.KEEP_LARGEST : self.keep_largest,
            self.KEEP_NEWEST : self.keep_newest
        }
        # assign desired method to handler
        self.handler = options.get(method, self.REPLACE)

    def should_replace(self, orig_file, new_file):
        return self.handler(orig_file, new_file)

    def skip(self, orig_file, new_file):
        return False
    def replace(self, orig_file, new_file):
        return True
    def keep_largest(self, orig_file, new_file):
        return new_file.is_bigger_than(orig_file)
    def keep_newest(self, orig_file, new_file):
        return new_file.is_newer_than(orig_file)

class error_codes():
    OK = 0
    ERROR = 1