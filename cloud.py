#encoding:UTF-8

class Cloud(object):

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

    # create directory on  server (aka mkdir -p)
    def mkdir(self, path):
        raise NotImplementedError()

