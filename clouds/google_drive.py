#encoding:UTF-8
import httplib2
#from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from clouds.GoogleApiPython3x.apiclient import errors
from clouds.GoogleApiPython3x.apiclient.discovery import build
from clouds.GoogleApiPython3x.apiclient.http import MediaFileUpload

import sys
import os.path

from cloud import Cloud
from utils import File, split_filepath

import xml.etree.cElementTree as xml

from oauth2client.client import flow_from_clientsecrets


REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
GOOGLE_DIR_MTYPE = 'application/vnd.google-apps.folder'
SCOPES = ['https://www.googleapis.com/auth/drive']

"""
'https://www.googleapis.com/auth/drive.file'
'https://www.googleapis.com/auth/drive.metadata.readonly',
'https://www.googleapis.com/auth/drive.readonly',
'https://www.googleapis.com/auth/drive.appdata',
'https://www.googleapis.com/auth/drive'
"""

class GoogleDrive(Cloud):
    #url = "www.googleapis.com/drive/v2"


    def __init__(self, secret_json_file, home_folder=''):
        super(GoogleDrive, self).__init__(home_folder)

        credential_file = secret_json_file + '.cred'
        if not os.path.isfile(credential_file):
             self._initial_auth_(secret_json_file, credential_file)

        self.drive_service = self._get_build_service_(secret_json_file, credential_file)

        self.dirs_cache = self._get_new_cache_level_('root')




    # list directory on server
    def _ls_(self, folder):
        folderId = self._get_folder_id_(folder)
        files = []

        def callback(children):
            for child in children.get('items', []):
                files.append(self._elem2file_(child))
            return

        if folderId is not None:
            param = {}
            param['q'] = "'%s' in parents" % folderId
            param['fields'] = 'items(createdDate,fileSize,id,mimeType,modifiedDate,originalFilename,title)'
            self._get_children_files_(callback, param)

        return files


    # download file from server
    def _download_(self, remote_file, local_file):
        file_id = self._get_file_id_(remote_file)

        if file_id is not None:
            print('Downloading '+ remote_file)
            try:
                file = self.drive_service.files().get(fileId=file_id).execute()
                content = self._download_file_(file)
                if content is not None:
                    with open(local_file, 'wb') as f:
                        f.write(content)
                        return local_file

            except errors.HttpError as error:
                print( 'An error occurred: %s' % error)
        return None



    # upload file to server
    def _upload_(self, local_file, remote_file):
        folder, filename = split_filepath(remote_file)
        self._mkdir_(folder)

        folder_id = self._get_folder_id_(folder)
        if folder_id is not None:
            print('Uploading '+ local_file)
            mtype = '*/*'
            media_body = MediaFileUpload(local_file, resumable=True, mimetype=mtype)

            body = {
                'title': filename,
                'mimeType': mtype,
                'parents': [{'id':folder_id}]
                }

            try:
                file = self.drive_service.files().insert(body=body, media_body=media_body).execute()

                # Uncomment the following line to print the File ID
                # print 'File ID: %s' % file['id']

                return 0
            except errors.HttpError as error:
                print('An error occured: %s' % error)
                #return None

        return 1

    # delete file or directory on  server
    def _delete_(self, filepath):
        file_id = self._get_file_id_(filepath)
        if file_id is not None:
            try:
                self.drive_service.files()._delete_(fileId=file_id).execute()
                return 0
            except errors.HttpError as error:
                print('An error occurred: %s' % error)
        return 1




    def _mkdir_(self, path):
        dirs = path.strip('/').split('/')

        # Check if path exists and update cache for max deepness
        if self._get_folder_id_(path) is None:
            cache_dir = self.dirs_cache
            for directory in dirs:
                print('Trying to create folder /' +directory)
                if cache_dir['children'] is None or directory not in cache_dir['children']:
                    response = self._create_dir_(cache_dir['id'], directory)
                    if response is not None:
                        id = response.get('id')
                        new_cache_dict = self._get_new_cache_level_(id)

                        if cache_dir['children'] is None: cache_dir['children'] = {}
                        cache_dir['children'][directory] = new_cache_dict
                    else:
                        return 1
                cache_dir=cache_dir['children'][directory]
        return 0

    # Code from Google example
    def _download_file_(self, drive_file):
        """Download a file's content.

          Args:
            service: Drive API service instance.
            drive_file: Drive File instance.

          Returns:
            File's content if successful, None otherwise.
        """
        download_url = drive_file.get('downloadUrl')
        if download_url:
            resp, content = self.drive_service._http.request(download_url)
            if resp.status == 200:
                print('Status: %s' % resp)
                return content
            else:
                print('An error occurred: %s' % resp)
                return None
        else:
            # The file doesn't have any content stored on Drive.
            return None


    def _create_dir_(self, parentId, folder_name):
        body = {
            'title': folder_name,
            'mimeType': GOOGLE_DIR_MTYPE,
            'parents' : [{'id':parentId}]
        }
        try:
            result = self.drive_service.files().insert(body=body).execute()
            return result
        except errors.HttpError as error:
            print('An error occured: %s' % error)
            return None

    # return id for last folder in path or None if
    # path does not exist
    def _get_folder_id_(self, path):
        if path == '' or path == '/':
            return 'root'
        #remove first and last slashes and split
        path_list = path.strip('/').split('/')

        curr_dir_id = 'root'
        curr_cache_level = self.dirs_cache
        for p in path_list:
            if curr_cache_level['children'] is None:
                curr_cache_level['children'] = self._get_children_dirs_(curr_dir_id)

            if p in curr_cache_level['children']:
                curr_cache_level = curr_cache_level['children'][p]
                curr_dir_id = curr_cache_level['id']
            else:
                return None
        return curr_dir_id

    # return dict of folders that are inside given one
    def _get_children_dirs_(self, folderId):
        dirs = {}

        param = {}
        param['q'] = "mimeType = '%s' and '%s' in parents" % (GOOGLE_DIR_MTYPE, folderId)
        param['fields'] = 'items(id,title)'


        def callback(children):
            for child in children.get('items', []):
                _name = child['title']
                _id = child['id']
                dirs[_name] = self._get_new_cache_level_(_id)
            return

        self._get_children_files_(callback, param)

        return dirs

    # calls callback function for each chunk of files obj (include folders)
    def _get_children_files_(self, callback, params={}):
        page_token = None
        while True:
            try:
                if page_token:
                    params['pageToken'] = page_token
                children = self.drive_service.files().list(**params).execute()

                callback(children)

                page_token = children.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError as error:
                print('An error occurred: %s' % error)
                break

    def _get_file_id_(self, filepath):
        folder, filename = split_filepath(filepath)

        # Trying to get fileid
        file_id = None
        files = self._ls_(folder)
        for file in files:
            if file.name == filename:
                file_id = file.id
                break
        return file_id

    def _elem2file_(self, elem):
        id = elem.get('id', None)
        name = elem.get('title', '')
        #orig_name = elem.get('originalFilename', '')
        mtype = elem.get('mimeType', '')
        size = elem.get('fileSize', 0)
        mtime = elem.get('modifiedDate', '')
        ctime = elem.get('createdDate', '')

        if mtype == GOOGLE_DIR_MTYPE:
            mtype = File.DIRECTORY_MTYPE
        return File(id, name, mtype, size, mtime, ctime)

    # User needs to open link in web browser to get secret code
    def _initial_auth_(self, secret_json, credfile):
        flow = flow_from_clientsecrets(secret_json, SCOPES, REDIRECT_URI)
        authorize_url = flow.step1_get_authorize_url()
        print('Go to the following link in your browser: \n' + authorize_url)
        code = input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage = Storage(credfile)
        storage.put(credentials)
        #print("All finished initializing, run again")


    def _get_build_service_(self, secret_json_file, credential_file):
        storage = Storage(credential_file)
        creds = storage.get()
        flow = flow_from_clientsecrets(secret_json_file,SCOPES)

        http = httplib2.Http()
        http = creds.authorize(http)
        return build('drive', 'v2', http=http)

    # creates a new dict that needed to store caches of brunches of directory tree
    def _get_new_cache_level_(self, id, children=None):
        return {'id':id, 'children':children}
