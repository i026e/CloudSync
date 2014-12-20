#encoding:UTF-8
import os
from utils import conflict_resolver, find_index, rand_str

class transloader():
    def __init__(self, source_cloud, dest_cloud):
        self.source = source_cloud
        self.dest = dest_cloud


    def transload(self, confl_resol_method, temp_dir = './temp'):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir
        self.log_file = os.path.join(temp_dir, 'log')
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
                    self.log("Folder with name " + src_f_path)
                else:
                    # check if file exists
                    index = find_index(dst_files_pathes, src_f_path)
                    # proceed if file does not exist or by conflict resolver allow
                    if index is None or conf_resolver.should_replace(dst_files[index][1], src_f):
                        print(index)
                        self.copy_file(src_f_path)

    def copy_file(self, src_file_path):
        temp_file_name = os.path.join(self.temp_dir, rand_str())

        result = self.source.download(src_file_path, temp_file_name)

        if result is not None:
            print(src_file_path)
            self.dest.upload(temp_file_name, src_file_path)
            try:
                os.remove(temp_file_name)
                
            except:
                pass
        else:
            self.log(src_file_path)


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
        print(text)


class uploader():
    def __init__(self):
        pass

class downloader():
    def __init__(self):
        pass
