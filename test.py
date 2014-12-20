#encoding:UTF-8

#import sys
#sys.path.append('clouds')
import clouds.yandex_disk as YaDisk
import clouds.google_drive as GDrive
import utils
from operations import transloader

def main():

    ya_disk = YaDisk.YandexDisk('./secrets/yandex.json', '/eyadisk')
    gdrive = GDrive.GoogleDrive('./secrets/google.json', '/eyadisk')

    trans = transloader(ya_disk, gdrive)
    gdrive.upload('./README.md', 'README.MD')


    #trans.transload(utils.conflict_resolver.REPLACE)

    #api.mkdir('/eyadisk/t/t/t/t/t/t')
    #api._upload_('./README.md', '/eyadisk222/rrrr/README.MD')
    #print(api.publish('/eyadisk/README.MD'))

    #
    # files = gdrive.ls('/Documents/')
    # for f in files:
    #     print(f.name+' '+f.mtype)
    #
    # print(gdrive.dirs_cache)
    #gdrive.mkdir('ervwrbrbtrthnrnryn22/rberbtybetb/rebtbetytnt5n/tb4t4tn4yn4yn')
    #gdrive.upload('/home/pavel/workspace/CloudsSync/README.md', 'ervwrbrbtrthnrnryn22/rberbtybetb/rebtbetytnt5n/tb4t4tn4yn4yn/README.md')
    #gdrive.download('Обои для рабочего стола.jpg', './2009')

if __name__ == '__main__':
	main()