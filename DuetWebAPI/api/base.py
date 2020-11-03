from typing import Dict, List
import requests
import os
import logging


class DuetAPI:
    def __init__(self, base_url) -> None:
        self._base_url = base_url

    def get_model(self, key: str = None) -> Dict:
        raise NotImplementedError

    def post_code(self, code: str) -> Dict:
        raise NotImplementedError

    def get_file(self, filename: str, directory: str = 'gcodes') -> str:
        raise NotImplementedError

    def put_file(self, file: str, directory: str = 'gcodes') -> Dict:
        raise NotImplementedError

    def get_fileinfo(self, filename: str = None, directory: str = 'gcodes') -> Dict:
        raise NotImplementedError

    def delete_file(self, filename: str, directory: str = 'gcodes') -> Dict:
        raise NotImplementedError

    def move_file(self, from_path: str, to_path: str, force: bool = False) -> Dict:
        raise NotImplementedError

    def get_directory(self, directory: str) -> List[Dict]:
        raise NotImplementedError

    def put_directory(self, directory: str) -> Dict:
        raise NotImplementedError
