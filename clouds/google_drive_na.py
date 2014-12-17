#encoding:UTF-8
import httplib2
#from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from clouds.GoogleApiPython3x.apiclient.discovery import build
import sys
import os.path

from clouds.cloud import Cloud
from http_request import request

import base64
import xml.etree.cElementTree as xml
from io import StringIO, BytesIO

from oauth2client.client import SignedJwtAssertionCredentials, flow_from_clientsecrets


SERVICE_ACCOUNT_EMAIL = "1041559596789-pc8rpa4ieuqo6ettui2dcsk1rjen23aq@developer.gserviceaccount.com"
REDIRECT_URI = 'http://localhost:8080'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
SERVICE_ACCOUNT_PKCS12_FILE_PATH = "/home/pavel/workspace/CloudsSync/secrets/privatekey.pem"
SCOPES = [
          'https://www.googleapis.com/auth/drive.file',
          ]

"""
'https://www.googleapis.com/auth/drive.metadata.readonly',
'https://www.googleapis.com/auth/drive.readonly',
'https://www.googleapis.com/auth/drive.appdata',
'https://www.googleapis.com/auth/drive'
"""
class GoogleDrive(Cloud):
    url = "www.googleapis.com/drive/v2"



    def __init__(self, secret_json_file):

        credential_file = secret_json_file + '.cred'
        if not os.path.isfile(credential_file):
             self.initial_auth(secret_json_file, credential_file)

        self.drive_service = self.get_build_service(secret_json_file, credential_file)

        #self.drive_service = self.createDriveService("klevpaul@gmail.com")
        #result = self.drive_service.request('https://www.googleapis.com/auth/drive/v2/files', 'GET')
        result = self.drive_service.files().list(corpus="DEFAULT").execute()
        print(result)

    # list directory on server
    def ls(self, folder):
        self.request.set_headers('folder_status')
        print(self.request.all_headers['Authorization'])
        resp = self.request.send_request('GET', '/files' )
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

    def initial_auth(self, secret_json, credfile):
        flow = flow_from_clientsecrets(secret_json, 'https://www.googleapis.com/auth/drive', REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: \n' + authorize_url)
        code = input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage = Storage(credfile)
        storage.put(credentials)
        print("All finished initializing, run again")


    def get_build_service(self, secret_json_file, credential_file):
        storage = Storage(credential_file)
        creds = storage.get()
        flow = flow_from_clientsecrets(secret_json_file,SCOPES)

        http = httplib2.Http()
        http = creds.authorize(http)
        return build('drive', 'v2', http=http)

    def createDriveService(self, user_email):

        """Build and returns a Drive service object authorized with the service accounts
        that act on behalf of the given user.

        Args:
          user_email: The email of the user.
        Returns:
          Drive service object.
        """
        f = open(SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
        key = f.read()
        f.close()

        credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL, key, scope=SCOPES, sub=user_email)

        http = httplib2.Http()
        http = credentials.authorize(http)
        #return http

        return build('drive', 'v2', http=http)


