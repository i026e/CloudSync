#encoding:UTF-8
from collections import namedtuple

class Cloud(object):
    File = namedtuple('File', ['name','id', "mtype",'size', 'mtime', 'ctime'])

    # list directory on server
    def ls(self, folder):
        raise NotImplementedError()

    # download file from server
    def download(self, remote_file, local_file):
        raise NotImplementedError()

    # upload file to server
    def upload(self, local_file, remote_file):
        raise NotImplementedError()

    # delete file or directory on  server
    def delete(self, remote_file):
        raise NotImplementedError()

    # publish file
    def publish(self, path):
        raise NotImplementedError()

    # unpublish file
    def unpublish(self, path):
        raise NotImplementedError()

    # create directory on  server
    def mkdir(self, folder):
        raise NotImplementedError()

    # create dirs on server (aka mkdir -p)
    def mkdirs(self, path):
        dirs = [d for d in path.split('/') if d]
        if not dirs:
            return
        if path.startswith('/'):
            dirs[0] = '/' + dirs[0]
        old_cwd = self.cwd
        try:
            for dir in dirs:
                self.mkdir(dir)
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