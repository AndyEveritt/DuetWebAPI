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
import logging
from typing import Dict, List

import requests

from DuetWebAPI.api import DSFAPI, DWCAPI, DuetAPI


class DuetWebAPIFactory:
    def __init__(self) -> None:
        self._creators = {}

    def __call__(self, base_url: str) -> DuetAPI:
        api = self.get_api(base_url)
        wrapper = self.create_wrapper(api)
        return wrapper(base_url)

    def register_api(self, name: str, creator: object, url_suffix: str) -> None:
        self._creators[name] = {'creator': creator, 'url_suffix': url_suffix}

    def get_api(self, base_url) -> DuetAPI:
        for api in self._creators.values():
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
        class DuetAPIWrapper(creator):
            def get_coords(self):
                model = self.get_model()
                axes = model['move']['axes']
                ret = {}
                for i in range(0, len(axes)):
                    ret[axes[i]['letter']] = axes[i]['userPosition']
                return(ret)

            def get_layer(self):
                model = self.get_model()
                layer = model['job']['layer']
                if not layer:
                    layer = 0
                return(layer)

            def get_num_extruders(self):
                model = self.get_model()
                extruders = model['move']['extruders']
                return len(extruders)

            def get_num_tools(self):
                model = self.get_model()
                tools = model['tools']
                return len(tools)

            def get_status(self):
                model = self.get_model()
                status = model['state']['status']
                return status

            def get_temperatures(self):
                model = self.get_model()
                sensors = model['sensors']['analog']
                return sensors

        return DuetAPIWrapper


DuetWebAPI = DuetWebAPIFactory()
DuetWebAPI.register_api('DWC', DWCAPI, '/rr_model')
DuetWebAPI.register_api('DSF', DSFAPI, '/machine/status')
