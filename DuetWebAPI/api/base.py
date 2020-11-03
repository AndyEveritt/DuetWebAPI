from typing import Dict, List
import requests
import os
import logging


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