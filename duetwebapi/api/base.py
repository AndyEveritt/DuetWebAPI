from typing import Dict, List, Union
from io import StringIO, TextIOWrapper, BytesIO
import requests
import os
import logging

# (connect, read) seconds. Reads are given a generous budget because some codes
# legitimately take a long time to reply, but they are no longer unbounded.
DEFAULT_TIMEOUT = (5, 60)


class TimeoutSession(requests.Session):
    """ A Session that applies a default timeout to every request.

    requests has no default timeout, so a board that stops responding part way
    through a request blocks the caller forever. Passing timeout= to an individual
    call still overrides this.
    """

    def __init__(self, timeout=DEFAULT_TIMEOUT) -> None:
        super().__init__()
        self.timeout = timeout

    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        return super().request(*args, **kwargs)


class DuetAPI:
    api_name = ''

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT) -> None:
        self.session = TimeoutSession(timeout)
        self.session_key = None
        self.base_url = base_url

    def __repr__(self):
        return f"DuetWebAPI('{self.base_url}') - {self.api_name}"

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

    def get_model(self, key: str = None, **kwargs) -> Dict:
        """ Get Duet object model. RRF3 only """
        raise NotImplementedError

    def send_code(self, code: str, **kwargs) -> Dict:
        """ Send G/M/T-code to Duet and return its reply """
        raise NotImplementedError

    def get_file(self, filename: str, directory: str = 'gcodes', binary: bool = False) -> str:
        """ Get file from Duet """
        raise NotImplementedError

    def upload_file(self, file: Union[str, bytes, StringIO, TextIOWrapper, BytesIO], filename: str, directory: str = 'gcodes') -> Dict:
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
