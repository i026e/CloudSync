#encoding:UTF-8
import os
from utils import conflict_resolver, find_index, rand_str, error_codes

ERROR_MESSAGES = {'fold':'folder exists: ',
                  'file':'file exists: ',
                  'down':'error while downloading file: ',
                  'up':'error while uploading file: ',
                  'local_rm':'error while removing local file: '}

class transloader():
    def __init__(self, source_cloud, dest_cloud,temp_dir = './temp'):
        self.source = source_cloud
        self.dest = dest_cloud
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir
        self.log_file = os.path.join(temp_dir, 'errors.log')

        log_head = """
***
Source: %s; Home: %s
Destination: %s; Home: %s
"""
        self.log(log_head %(source_cloud.__class__.__name__, source_cloud.home_folder,
                            dest_cloud.__class__.__name__, dest_cloud.home_folder))


    def transload(self, confl_resol_method):
        conf_resolver = conflict_resolver(confl_resol_method)

        directories = ['/']
        while len(directories) > 0:
            curr_dir = directories.pop(0)
            #print(directories)#'Process ' + curr_dir)
            src_dirs, src_files = self.get_child_dirs_files(self.source, curr_dir)

            directories += src_dirs

            # ensure  that directory exists on the destination server
            self.dest.mkdir(curr_dir)

            dst_dirs, dst_files = self.get_child_dirs_files(self.dest, curr_dir)
            dst_files_pathes = [path for (path, file) in dst_files]

            for src_f_path, src_f in src_files:
                # check if folder with such name exists
                if src_f_path in dst_dirs:
                    self.log(ERROR_MESSAGES['fold'] + src_f_path)
                else:
                    # check if file exists
                    index = find_index(dst_files_pathes, src_f_path)
                    # proceed if file does not exist or by conflict resolver allow
                    if index is None or conf_resolver.should_replace(dst_files[index][1], src_f):
                        self.copy_file(src_f_path)
                    else:
                        self.log(ERROR_MESSAGES['file'] + src_f_path)

    def copy_file(self, src_file_path):
        temp_file_name = os.path.join(self.temp_dir, rand_str())

        result = self.source.download(src_file_path, temp_file_name)

        if result is None:
            self.log(ERROR_MESSAGES['down'] + src_file_path)
        else:
            result = self.dest.upload(temp_file_name, src_file_path)
            if result != error_codes.OK:
                self.log(ERROR_MESSAGES['up'] + src_file_path)

            try:
                os.remove(temp_file_name)
            except:
                self.log(ERROR_MESSAGES['local_rm'] + temp_file_name)

    def get_child_dirs_files(self, cloud, curr_dir):
        dirs = []
        files = []

        listing = cloud.ls(curr_dir)
        for element in listing:
            path = (curr_dir + '/' + element.name).strip('/')
            if element.is_dir():
                dirs.append(path)
            else:
                files.append((path,element))
        return dirs, files

    def log(self, text):
        with open(self.log_file, 'a') as lf:
            lf.write(text+'\n')



class uploader():
    def __init__(self):
        pass

class downloader():
    def __init__(self):
        pass
