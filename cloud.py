#encoding:UTF-8

class Cloud(object):

    def __init__(self, home_folder):
        self.home_folder = home_folder.strip('/')
        if len(self.home_folder) > 0:
            self.home_folder = '/' + self.home_folder + '/'

        else:
            self.home_folder = '/'

    #public methods
    def ls(self, folder):
        return self._ls_(self.full_path(folder))
    # download file from server
    def download(self, remote_file, local_file):
        return self._download_(self.full_path(remote_file), local_file)
    # upload file to server
    def upload(self, local_file, remote_file):
        return self._upload_(local_file, self.full_path(remote_file))
    # delete file or directory on  server
    def delete(self, remote_file):
        return self._delete_(self.full_path(remote_file))
    # create directory on  server (aka mkdir -p)
    def mkdir(self, path):
        return self._mkdir_(self.full_path(path))

    def full_path(self, path):
        return self.home_folder + path.strip('/')

    #private methods to be  implemented

    # list directory on server
    def _ls_(self, folder):
        raise NotImplementedError()

    # download file from server
    def _download_(self, remote_file, local_file):
        raise NotImplementedError()

    # upload file to server
    def _upload_(self, local_file, remote_file):
        raise NotImplementedError()

    # delete file or directory on  server
    def _delete_(self, remote_file):
        raise NotImplementedError()

    # create directory on  server (aka mkdir -p)
    def _mkdir_(self, path):
        raise NotImplementedError()

