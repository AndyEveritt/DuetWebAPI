import logging
import os
from typing import Dict, List, Union
from io import StringIO, TextIOWrapper

import requests

from .base import DuetAPI


class DWCAPI(DuetAPI):
    """
    Duet Web Control REST API Interface.

    Used with a Duet 2/3 in standalone mode.
    Must use RRF3.
    """
    api_name = 'DWC_REST'

    def connect(self, password=''):
        """ Start connection to Duet """
        url = f'{self.base_url}/rr_connect'
        r = requests.get(url, {'password': password})
        if not r.ok:
            raise ValueError
        return r.json()

    def disconnect(self):
        """ End connection to Duet """
        url = f'{self.base_url}/rr_disconnect'
        r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.json()

    def get_model(self, key: str = None) -> Dict:
        url = f'{self.base_url}/rr_model'
        r = requests.get(url, {'flags': 'd99vn', 'key': key})
        if not r.ok:
            raise ValueError
        j = r.json()
        return j['result']

    def _get_reply(self) -> Dict:
        url = f'{self.base_url}/rr_reply'
        r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.text

    def send_code(self, code: str) -> Dict:
        url = f'{self.base_url}/rr_gcode'
        r = requests.get(url, {'gcode': code})
        if not r.ok:
            raise ValueError
        reply = self._get_reply()
        return {'response': reply}

    def get_file(self, filename: str, directory: str = 'gcodes') -> str:
        """
        filename: name of the file you want to download including extension
        directory: the folder that the file is in, options are ['gcodes', 'macros', 'sys']

        returns the file as a string
        """
        url = f'{self.base_url}/rr_download'
        r = requests.get(url, {'name': f'/{directory}/{filename}'})
        if not r.ok:
            raise ValueError
        return r.text

    def upload_file(self, file: Union[StringIO, TextIOWrapper], filename: str, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_upload?name=/{directory}/{filename}'
        r = requests.post(url, data=file)
        if not r.ok:
            raise ValueError
        return r.json()

    def get_fileinfo(self, filename: str = None, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_fileinfo'
        if filename:
            r = requests.get(url, {'name': f'/{directory}/{filename}'})
        else:
            r = requests.get(url)
        if not r.ok:
            raise ValueError
        return r.json()

    def delete_file(self, filename: str, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_delete'
        r = requests.get(url, {'name': f'/{directory}/{filename}'})
        if not r.ok:
            raise ValueError
        return r.json()

    def move_file(self, from_path, to_path, **_ignored):
        # BUG this doesn't work currently
        raise NotImplementedError
        url = f'{self.base_url}/rr_move'
        r = requests.get(url, {'old': f'{from_path}', 'new': f'{to_path}'})
        if not r.ok:
            raise ValueError
        return r.json()

    def get_directory(self, directory: str) -> List[Dict]:
        url = f'{self.base_url}/rr_filelist'
        r = requests.get(url, {'dir': f'/{directory}'})
        if not r.ok:
            raise ValueError
        return r.json()['files']

    def create_directory(self, directory: str) -> Dict:
        url = f'{self.base_url}/rr_mkdir'
        r = requests.get(url, {'dir': f'/{directory}'})
        if not r.ok:
            raise ValueError
        return r.json()
