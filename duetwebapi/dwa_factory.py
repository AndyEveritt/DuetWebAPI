# Python Script containing a class to send commands to, and query specific information from,
#   Duet based printers running Duet RepRap V3 firmware.
#
# Does NOT hold open the connection.  Use for low-volume requests.
# Does NOT, at this time, support Duet passwords.
#
# Copyright (C) 2020 Andy Everitt all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#
# Requires Python3

import logging
from typing import Dict, List

import requests

from .api import DSFAPI, DWCAPI, DuetAPI, DuetAPIWrapper


class DuetWebAPIFactory:
    def __init__(self) -> None:
        self._creators = {}

    def __call__(self, base_url: str):
        Api = self.get_api(base_url)
        Wrapper = self.create_wrapper(Api)
        return Wrapper(base_url)

    def register_api(self, name: str, creator: object, url_suffix: str) -> None:
        self._creators[name] = {'creator': creator, 'url_suffix': url_suffix}

    def get_api(self, base_url) -> DuetAPI:
        for api in self._creators.values():
            if not base_url.startswith('http://'):
                base_url = f'http://{base_url}'
            url = base_url + api['url_suffix']
            try:
                r = requests.get(url, timeout=(2, 60))
            except requests.exceptions.ConnectionError:
                continue
            if r.ok:
                creator = api['creator']
                return creator

        logging.error(f'Can not get API for {base_url}')
        raise ValueError

    def create_wrapper(self, creator: DuetAPI):
        Wrapper = type('DuetWebAPI', (DuetAPIWrapper, creator), {})

        return Wrapper


DuetWebAPI = DuetWebAPIFactory()
DuetWebAPI.register_api(DWCAPI.api_name, DWCAPI, '/rr_model')
DuetWebAPI.register_api(DSFAPI.api_name, DSFAPI, '/machine/status')
