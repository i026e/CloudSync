#encoding:UTF-8

import clouds.yandex_disk as YaDisk
import clouds.google_drive as GDrive
from utils import conflict_resolver
from operations import transloader


def main():
    # create source and destination objects, enter path to home folder
    # only files in that folder will be uploaded
    source = YaDisk.YandexDisk('./secrets/yandex.json', '/test123')
    destination = GDrive.GoogleDrive('./secrets/google.json', '/test123')

    # choose what to do if file with the same name already exists
    # for example skip uploading, or replace
    # for all possible variants see utils.conflict_resolver
    conflict_method = conflict_resolver.SKIP

    #start the process
    trans = transloader(source, destination)
    trans.transload(conflict_method)


if __name__ == '__main__':
	main()