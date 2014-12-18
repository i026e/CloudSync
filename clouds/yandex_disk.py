import base64
import xml.etree.cElementTree as xml

from cloud import Cloud
from utils import http_request, get_json_from_file, File



class YandexDisk(Cloud):
    webdav_url = "webdav.yandex.ru"
    def __init__(self, credfile):
        creds = get_json_from_file(credfile)
        token, user, pwd =creds.get("token"), creds.get("user"), creds.get("pwd")


        auth = ''
        if token:
            auth = 'OAuth %s' % token
        elif user and pwd:
            b_auth = bytes('%s:%s' % (user, pwd), 'UTF-8')
            auth = 'Basic %s' % base64.b64encode(b_auth).decode('UTF-8')
        else:
            raise Exception()

        self.request = http_request(self.webdav_url, auth)
        self.last_id = 0

    # list directory on server
    def ls(self, folder):
        self.request.set_headers('folder_status')
        print(self.request.all_headers['Authorization'])
        resp = self.request.send_request('PROPFIND', '/%s' % folder)
        resp_data = xml.fromstring(resp['data']) #.parse(BytesIO(resp['data']))
        #print(xml.tostring(resp_data, encoding='utf8', method='xml'))
        return [self.elem2file(elem) for elem in resp_data.findall('{DAV:}response')]

    # download file from server
    def download(self, remote_file, local_file):
        self.request.set_headers('download')
        resp = self.request.send_request('GET', '/%s' % remote_file)
        with open(local_file, 'wb') as f:
            f.write(resp['data'])

    # upload file to server
    def upload(self, local_file, remote_file):
        f = open(local_file, 'rb')
        data = f.read()
        self.request.set_headers('upload', len(data))
        resp = self.request.send_request('PUT', remote_file, data)
        f.close()

    # delete file or directory on  server
    def delete(self, file):
        self.request.set_headers('common')
        resp = self.request.send_request('DELETE', '/%s' % file)

    # publish file
    def publish(self, path):
        self.request.set_headers('common')
        resp = self.request.send_request('POST', '/%s' % path + '?publish')
        if resp['status'] != 302:
            raise Exception('Wtf?')
        location = ''
        for key, v in resp['headers']:
            if key == 'location':
                location = v
                break
        return location


    # unpublish file
    def unpublish(self, path):
        self.request.set_headers('common')
        resp = self.request.send_request('POST', '/%s' % path + '?unpublish')

    # create directory on  server
    def mkdir_dir(self, folder):
        self.request.set_headers('common')
        resp = self.request.send_request('MKCOL', '/%s' % folder)


    # create dirs on server (aka mkdir -p)
    def mkdir(self, path):
        dirs = [d for d in path.split('/') if d]
        if not dirs:
            return
        if path.startswith('/'):
            dirs[0] = '/' + dirs[0]
        old_cwd = self.cwd
        try:
            for dir in dirs:
                self.mkdir_dir(dir)
                self.cd(dir)
        finally:
            self.cd(old_cwd)

    # helper for mkdirs - make path on server
    def cd(self, path):
        path = path.strip()
        if not path:
            return
        stripped_path = '/'.join(part for part in path.split('/') if part) + '/'
        if stripped_path == '/':
            self.cwd = stripped_path
        elif path.startswith('/'):
            self.cwd = '/' + stripped_path
        else:
            self.cwd += stripped_path




    def elem2file(self, elem):
        name = self.prop(elem, 'href')
        id = self.last_id
        mtype = self.prop(elem, 'getcontenttype', File.DIRECTORY_MTYPE)
        size = int(self.prop(elem, 'getcontentlength', 0))
        mtime = self.prop(elem, 'getlastmodified', '')
        ctime = self.prop(elem, 'creationdate', '')

        self.last_id += 1
        return File(id, name, mtype, size, mtime, ctime)


    def prop(self, elem, name, default=None):
        child = elem.find('.//{DAV:}' + name)
        return default if child is None else child.text
