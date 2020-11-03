#!/usr/bin/env python3
from DuetWebAPI import DuetWebAPI as DWA
import json

# Test cases


riley = DWA('http://riley')
force_rig = DWA('http://forcerig')
force_rig.api_name
force_rig.put_file('test.gcode')
riley.put_file('test.gcode')
pass
