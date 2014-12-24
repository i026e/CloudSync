Transfer your files from one cloud to another
=============================================

Utility to copy files from one cloud storage to another

Features
--------

Currently supports Yandex.Disk And Google.Drive

Requirements
------------

Python 3


pip3 install --upgrade python-dateutil oauth2client


Also there is some bug with byte strings processing in httplib2
(it was automatically installed with oauth2client)
so please reinstall it from https://github.com/i026e/httplib2


pip3 uninstall httplib2
pip3 install --upgrade https://github.com/i026e/httplib2/archive/master.zip

or manually change the 194 line of /usr/local/lib/python3.x/dist-packages/httplib2/__init__.py

from:

def _normalize_headers(headers):
    return dict([ (key.lower(), NORMALIZE_SPACE.sub(value, ' ').strip()) for (key, value) in headers.items()])

to:

def _normalize_headers(headers):
    return dict([ (_convert_byte_str(key).lower(), NORMALIZE_SPACE.sub(_convert_byte_str(value), ' ').strip()) for (key, value) in headers.items()])
def _convert_byte_str(s):
    if not isinstance(s, str):
        return str(s, 'utf-8')
    return s



For now there is no official google-api-python-client for Python 3 so I keep an unofficial version locally


Quick Start
-----------
Open ./secrets folder.
Copy yandex.json.example to yandex.json
Enter your login and password to yandex.json

if you want to use Google Drive you need to get Google API key
See instructions how to do that: https://github.com/i026e/CloudSync/blob/master/How%20to%20get%20Google%20API%20Key

Edit run.py:
Select source & destination

Run it




