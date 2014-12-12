#encoding:UTF-8
from clouds.cloud import Cloud
from http_request import request

import base64
import xml.etree.cElementTree as xml
from io import StringIO, BytesIO

class GoogleDrive(Cloud):
    webdav_url = "www.googleapis.com/drive/v2"
    def __init__(self, token=None, user=None, pwd=None):
        auth = ''
        if token:
            auth = 'OAuth %s' % token
        elif user and pwd:
            b_auth = bytes('%s:%s' % (user, pwd), 'UTF-8')
            auth = 'Basic %s' % base64.b64encode(b_auth).decode('UTF-8')
        else:
            raise Exception()

        self.request = request(self.webdav_url, auth)

    # list directory on server
    def ls(self, folder):
        self.request.set_headers('folder_status')
        print(self.request.all_headers['Authorization'])
        resp = self.request.send_request('PROPFIND', '/%s' % folder)
        resp_data = xml.fromstring(resp['data']) #.parse(BytesIO(resp['data']))
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
        self._set_headers('common')
        resp = self.request.send_request('POST', '/%s' % path + '?unpublish')

    # create directory on  server
    def mkdir(self, folder):
        self._set_headers('common')
        resp = self.request.send_request('MKCOL', '/%s' % folder)

    


    def elem2file(self, elem):
        return self.File(
            self.prop(elem, 'href'),
            int(self.prop(elem, 'getcontentlength', 0)),
            self.prop(elem, 'getlastmodified', ''),
            self.prop(elem, 'creationdate', ''),
        )

    def prop(self, elem, name, default=None):
        child = elem.find('.//{DAV:}' + name)
        return default if child is None else child.text
