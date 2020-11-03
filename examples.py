#!/usr/bin/env python3
from duetwebapi import DuetWebAPI as DWA
import json

###################################
# Create API link
###################################
riley = DWA('http://riley')
bruce = DWA('http://bruce')

###################################
# REST API methods
###################################
riley.get_model()
bruce.get_model()

riley.send_code('M115')
bruce.send_code('M115')

riley.upload_file('test.gcode')
bruce.upload_file('test.gcode')

riley.get_file('test.gcode')
bruce.get_file('test.gcode')

riley.move_file('gcodes/test.gcode', 'gcodes/test2.gcode')
# bruce.move_file('gcodes/test.gcode', 'gcodes/test2.gcode')

riley.delete_file('test2.gcode')
bruce.delete_file('test2.gcode')

riley.get_directory('gcodes')
bruce.get_directory('gcodes')

###################################
# Wrapper methods
###################################
riley.get_coords()
bruce.get_coords()

riley.get_layer()
bruce.get_layer()

riley.get_num_extruders()
bruce.get_num_extruders()

riley.get_num_tools()
bruce.get_num_tools()

riley.get_status()
bruce.get_status()

riley.get_temperatures()
bruce.get_temperatures()
pass
