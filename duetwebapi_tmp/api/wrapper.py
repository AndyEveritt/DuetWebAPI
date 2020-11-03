import logging
from typing import Dict, List

from .base import DuetAPI


class DuetAPIWrapper(DuetAPI):
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
