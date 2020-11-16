import logging
from typing import Dict, List

from .base import DuetAPI


class DuetAPIWrapper(DuetAPI):
    def emergency_stop(self) -> None:
        self.send_code('M112')
        self.send_code('M999')

    def start_print(self, filename: str) -> Dict:
        return self.send_code(f'M32 "{filename}"')

    def pause_print(self) -> Dict:
        return self.send_code(f'M25')

    def stop_print(self, leave_heaters: bool = True) -> Dict:
        status = self.get_status()
        if status == 'idle':
            return
        if not status == 'paused':
            self.pause_print()

        code = 'M0'
        if leave_heaters:
            code += ' H1'
        return self.send_code(code)

    def get_coords(self) -> Dict:
        model = self.get_model()
        axes = model['move']['axes']
        ret = {}
        for i in range(0, len(axes)):
            ret[axes[i]['letter']] = axes[i]['userPosition']
        return(ret)

    def get_layer(self) -> int:
        model = self.get_model()
        layer = model['job']['layer']
        if not layer:
            layer = 0
        return(layer)

    def get_num_extruders(self) -> int:
        model = self.get_model()
        extruders = model['move']['extruders']
        return len(extruders)

    def get_num_tools(self) -> int:
        model = self.get_model()
        tools = model['tools']
        return len(tools)

    def get_status(self) -> str:
        model = self.get_model()
        status = model['state']['status']
        return status

    def get_temperatures(self) -> List[Dict]:
        model = self.get_model()
        sensors = model['sensors']['analog']
        return sensors

    def get_current_tool(self) -> int:
        model = self.get_model()
        tool = model['state']['currentTool']
        return tool

    def get_messagebox(self) -> Dict:
        model = self.get_model()
        messagebox = model['state']['messageBox']
        return messagebox

    def acknowledge_message(self, response: int = 0) -> Dict:
        return self.send_code(f'M292 P{response}')
