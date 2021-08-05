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
        axes = self.get_model(key='move.axes', verbose=False)
        ret = {}
        for i in range(0, len(axes)):
            ret[axes[i]['letter']] = axes[i]['userPosition']
        return(ret)

    def get_layer(self) -> int:
        layer = self.get_model(key='job.layer', verbose=False)
        if not layer:
            layer = 0
        return(layer)

    def get_num_extruders(self) -> int:
        extruders = self.get_model(key='move.extruders', verbose=False, depth=2)
        return len(extruders)

    def get_num_tools(self) -> int:
        tools = self.get_model(key='tools', verbose=False, depth=1)
        return len(tools)

    def get_status(self) -> str:
        status = self.get_model(key='state.status')
        return status

    def get_temperatures(self) -> List[Dict]:
        sensors = self.get_model(key='sensors.analog')
        return sensors

    def get_current_tool(self) -> int:
        tool = self.get_model(key='state.currentTool', verbose=False)
        return tool

    def get_messagebox(self) -> Dict:
        messagebox = self.get_model(key='state.messageBox')
        return messagebox

    def acknowledge_message(self, response: int = 0) -> Dict:
        return self.send_code(f'M292 P{response}')
