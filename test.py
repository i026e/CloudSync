__author__ = 'pavel'

#import sys
#sys.path.append('clouds')
#import clouds.yandex_disk as YaDisk
import clouds.google_drive as GDrive

def main():

    ya_user = ''
    ya_pwd = ''

    #api = YaDisk.YandexDisk(user=ya_user, pwd=ya_pwd)

    #print(api.ls('/'))

    #api.mkdir('eyadisk')
    #api.upload('./README.md', '/eyadisk/README.MD')
    #print(api.publish('/eyadisk/README.MD'))

    gdrive = GDrive.GoogleDrive('./secrets/google.json')


if __name__ == '__main__':
	main()