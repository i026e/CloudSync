import base64
import xml.etree.cElementTree as xml

from cloud import Cloud
from utils import *



class YandexDisk(Cloud):
    webdav_url = "webdav.yandex.ru"

    def __init__(self, credfile, home_folder=''):
        super(YandexDisk, self).__init__(home_folder)

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
    def _ls_(self, folder):
        folder = url_encode(folder)
        self.request.set_headers('folder_status')
        try:
            resp = self.request.send_request('PROPFIND', '/%s' % folder)
            resp_data = xml.fromstring(resp['data'])
            #print(xml.tostring(resp_data, encoding='utf8', method='xml'))
            # it also returns self name at 0th position
            return [self._elem2file_(elem) for elem in resp_data.findall('{DAV:}response')][1:]
        except Exception as e:
            print(self.__module__)
            print(e)
            return []

    # download file from server
    def _download_(self, remote_file, local_file):
        remote_file = url_encode(remote_file)
        self.request.set_headers('download')
        try:
            resp = self.request.send_request('GET', '/%s' % remote_file)
            with open(local_file, 'wb') as f:
                f.write(resp['data'])
            return local_file
        except Exception as e:
            print(self.__module__)
            print(e)
            return None

    # upload file to server
    def _upload_(self, local_file, remote_file):
        remote_file = url_encode(remote_file)
        folders, filename = split_filepath(remote_file)
        if len(folders) > 0:
            self._mkdir_(folders)
        f = open(local_file, 'rb')
        data = f.read()
        self.request.set_headers('upload', len(data))
        resp = self.request.send_request('PUT', remote_file, data)
        f.close()

        if resp['status'] == 201:
            return error_codes.OK
        return error_codes.ERROR

    # delete file or directory on  server
    def _delete_(self, file):
        file = url_encode(file)
        self.request.set_headers('common')

        resp = self.request.send_request('DELETE', '/%s' % file)

        # By documentation server must return 200 "OK", but also can get 204 "No Content".
        # Anyway file or directory have been removed.
        if resp['status'] in [200, 204]:
            return error_codes.OK
        return error_codes.ERROR

    # Not used
    # # publish file
    # def _publish_(self, path):
    #     path = url_encode(path)
    #     self.request.set_headers('common')
    #     resp = self.request.send_request('POST', '/%s' % path + '?publish')
    #     if resp['status'] != 302:
    #         raise Exception('Wtf?')
    #     location = ''
    #     for key, v in resp['headers']:
    #         if key == 'location':
    #             location = v
    #             break
    #     return location
    #
    #
    # # unpublish file
    # def _unpublish_(self, path):
    #     path = url_encode(path)
    #     self.request.set_headers('common')
    #     resp = self.request.send_request('POST', '/%s' % path + '?unpublish')

    # create directory on  server
    def _mkdir_dir_(self, folder):
        folder = url_encode(folder)
        self.request.set_headers('common')
        resp = self.request.send_request('MKCOL', '/%s' % folder)

        # possible "good" statuses
        # 201
        # 405 Path already exists
        if resp['status'] in [201, 405]:
            return error_codes.OK
        return error_codes.ERROR


    # create dirs on server (aka mkdir -p)
    def _mkdir_(self, path):
        path = url_encode(path)
        dirs = path.strip('/').split('/')
        path = ''
        for i in range(len(dirs)):
            path = path + '/' + dirs[i]
            result = self._mkdir_dir_(path)
            if result != error_codes.OK:
                return error_codes.ERROR
        return error_codes.OK


    def _elem2file_(self, elem):
        name = url_decode(self._prop_(elem, 'href').strip('/').split('/')[-1])
        id = self.last_id
        mtype = self._prop_(elem, 'getcontenttype', File.DIRECTORY_MTYPE)
        size = self._prop_(elem, 'getcontentlength', 0)
        mtime = self._prop_(elem, 'getlastmodified', '')
        ctime = self._prop_(elem, 'creationdate', '')

        self.last_id += 1
        return File(id, name, mtype, size, mtime, ctime)


    def _prop_(self, elem, name, default=None):
        child = elem.find('.//{DAV:}' + name)
        return default if child is None else child.text
