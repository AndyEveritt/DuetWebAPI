# Python Script containing a class to send commands to, and query specific information from,
#   Duet based printers running either Duet RepRap V2 or V3 firmware.
#
# Does NOT hold open the connection.  Use for low-volume requests.
# Does NOT, at this time, support Duet passwords.
#
# Not intended to be a gerneral purpose interface; instead, it contains methods
# to issue commands or return specific information. Feel free to extend with new
# methods for other information; please keep the abstraction for V2 V3
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#
# Requires Python3
from typing import Dict, List
import requests
import json
import sys
import datetime
import logging


class DuetWebAPIFactory:
    def __init__(self):
        self._creators = {}

    def register_api(self, name: str, creator: object, url_suffix: str):
        self._creators[name] = {'creator': creator, 'url_suffix': url_suffix}

    def get_api(self, base_url):
        for api in self._creators.values():
            url = base_url + api['url_suffix']
            r = requests.get(url, timeout=(2, 60))
            if r.ok:
                creator = api['creator']
                return creator(base_url)

        self.logging.error(f'Can not get API for {self.base_url}')
        raise ValueError


class DuetAPI:
    def __init__(self, base_url) -> None:
        self._base_url = base_url

    def get_model(self):
        raise NotImplementedError

    def post_code(self, code):
        raise NotImplementedError

    def get_file(self, filename, path):
        raise NotImplementedError

    def put_file(self, filename, path):
        raise NotImplementedError

    def get_fileinfo(self, filename):
        raise NotImplementedError

    def delete_file(self, filename):
        raise NotImplementedError

    def move_file(self, from_path, to_path, force=False):
        raise NotImplementedError

    def get_directory(self, directory):
        raise NotImplementedError

    def put_directory(self, directory):
        raise NotImplementedError


class DWCAPI(DuetAPI):
    def get_model(self, key=None) -> Dict:
        url = f'{self._base_url}/rr_model'
        r = requests.get(url, {'flags': 'd99vn', 'key': key})
        if not r.ok:
            raise ValueError
        j = r.json()
        return j['result']

    def post_code(self, code) -> Dict:
        url = f'{self._base_url}/rr_gcode'
        r = requests.get(url, {'gcode': code})
        if not r.ok:
            raise ValueError
        return r.json()

    def get_file(self, filename: str, directory: str = 'gcodes') -> str:
        """
        filename: name of the file you want to download including extension
        directory: the folder that the file is in, options are ['gcodes', 'macros', 'sys']

        returns the file as a string
        """
        url = f'{self._base_url}/rr_download'
        r = requests.get(url, {'name': f'/{directory}/{filename}'})
        if not r.ok:
            raise ValueError
        return r.text

    def put_file(self, file: str, duet_filename: str, directory: str = 'gcodes'):
        url = f'{self._base_url}/rr_upload?name=/{directory}/{duet_filename}'
        with open(file, 'rb') as f:
            r = requests.post(url, data=f)
        if not r.ok:
            raise ValueError
        return r.json()

    def get_fileinfo(self, filename):
        pass

    def delete_file(self, filename):
        pass

    def move_file(self, from_path, to_path, force=False):
        pass

    def get_directory(self, directory) -> List[Dict]:
        url = f'{self._base_url}/rr_filelist'
        r = requests.get(url, {'dir': f'/{directory}'})
        if not r.ok:
            raise ValueError
        return r.json()['files']

    def put_directory(self, directory):
        pass


class DSFAPI(DuetAPI):
    def get_model(self) -> Dict:
        url = f'{self._base_url}/machine/status'
        r = requests.get(url)
        j = r.json()
        return j

    def post_code(self, code) -> str:
        url = f'{self._base_url}/machine/code'
        r = requests.post(url, data=code)
        return r.text

    def get_file(self, filename, directory):
        """
        filename: name of the file you want to download including extension
        directory: the folder that the file is in, options are ['gcodes', 'macros', 'sys']

        returns the file as a string
        """
        url = f'{self._base_url}/machine/file/{directory}'
        r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.text

    def put_file(self, file: str, duet_filename: str, directory: str = 'gcodes'):
        # BUG this uploads an empty file
        url = f'{self._base_url}/machine/file/{directory}/{duet_filename}'
        with open(file, 'rb') as f:
            r = requests.put(url, data=f)
        if not r.ok:
            raise ValueError
        return r.ok

    def get_fileinfo(self, filename):
        pass

    def delete_file(self, filename):
        pass

    def move_file(self, from_path, to_path, force=False):
        pass

    def get_directory(self, directory) -> List[Dict]:
        url = f'{self._base_url}/machine/directory/{directory}'
        r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.json()

    def put_directory(self, directory):
        pass


factory = DuetWebAPIFactory()
factory.register_api('DWC', DWCAPI, '/rr_model')
factory.register_api('DSF', DSFAPI, '/machine/status')


riley = factory.get_api('http://riley')
force_rig = factory.get_api('http://forcerig')
force_rig.put_file('test.gcode', 'test.gcode')
riley.put_file('test.gcode', 'test.gcode')
pass
