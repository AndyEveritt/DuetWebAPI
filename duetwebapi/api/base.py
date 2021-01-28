from typing import Dict, List, Union
from io import StringIO, TextIOWrapper
import requests
import os
import logging


class DuetAPI:
    api_name = ''

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value: str):
        if not value.startswith('http://'):
            value = f'http://{value}'
        self._base_url = value

    def connect(self, **kwargs):
        """ Start connection to Duet """
        raise NotImplementedError

    def disconnect(self):
        """ End connection to Duet """
        raise NotImplementedError

    def get_model(self, key: str = None) -> Dict:
        """ Get Duet object model. RRF3 only """
        raise NotImplementedError

    def send_code(self, code: str) -> Dict:
        """ Send G/M/T-code to Duet """
        raise NotImplementedError

    def get_file(self, filename: str, directory: str = 'gcodes') -> str:
        """ Get file from Duet """
        raise NotImplementedError

    def upload_file(self, file: Union[StringIO, TextIOWrapper], filename: str, directory: str = 'gcodes') -> Dict:
        """ Upload file to Duet """
        raise NotImplementedError

    def get_fileinfo(self, filename: str = None, directory: str = 'gcodes') -> Dict:
        """ Get file info """
        raise NotImplementedError

    def delete_file(self, filename: str, directory: str = 'gcodes') -> Dict:
        """ Delete file on Duet """
        raise NotImplementedError

    def move_file(self, from_path: str, to_path: str, force: bool = False) -> Dict:
        """ Move file on Duet, can be used to rename files """
        raise NotImplementedError

    def get_directory(self, directory: str) -> List[Dict]:
        """ Get a list of all the files & directories in a directory """
        raise NotImplementedError

    def create_directory(self, directory: str) -> Dict:
        """ Create a new directory """
        raise NotImplementedError
