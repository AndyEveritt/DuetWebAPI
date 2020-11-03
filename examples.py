#!/usr/bin/env python3
from DuetWebAPI import DuetWebAPI as DWA
import json

###################################
# Create API link
###################################
riley = DWA('http://riley')
force_rig = DWA('http://forcerig')

###################################
# REST API methods
###################################
riley.get_model()
force_rig.get_model()

riley.post_code('M115')
force_rig.post_code('M115')

riley.put_file('test.gcode')
force_rig.put_file('test.gcode')

riley.get_file('test.gcode')
force_rig.get_file('test.gcode')

riley.move_file('gcodes/test.gcode', 'gcodes/test2.gcode')
# force_rig.move_file('gcodes/test.gcode', 'gcodes/test2.gcode')

riley.delete_file('test2.gcode')
force_rig.delete_file('test2.gcode')

riley.get_directory('gcodes')
force_rig.get_directory('gcodes')

###################################
# Wrapper methods
###################################
riley.get_coords()
force_rig.get_coords()

riley.get_layer()
force_rig.get_layer()

riley.get_num_extruders()
force_rig.get_num_extruders()

riley.get_num_tools()
force_rig.get_num_tools()

riley.get_status()
force_rig.get_status()

riley.get_temperatures()
force_rig.get_temperatures()
pass
