# DuetWebAPI
Python interface to Duet RepRap V3 firmware via Http REST API.

* Works over IP network.
* Does not support passwords on the printer. 
* Supported boards:
  * Duet 3 + SBC
  * Duet 3 standalone
  * Duet 2 standalone

# Install
```
pip install duetwebapi
```

Alternatively:
```
pip install -e "git+https://github.com/AndyEveritt/DuetWebAPI.git@master#egg=duetwebapi"
```

# Usage
* See 'examples.py' for examples. 

```python
from duetwebapi import DuetWebAPI

printer = DuetWebAPI(f'http://{printer_hostname}')
```

## REST API
The REST API allows for the following operations:

Method | Description
------ | -----------
`get_model(key: str = None) -> Dict` | Get Duet object model. RRF3 only
`send_code(code: str) -> Dict` | Send G/M/T-code to Duet
`get_file(filename: str, directory: str = 'gcodes') -> str` | Download file from Duet
`upload_file(file: StringIO | TextIOWrapper, filename: str, directory: str = 'gcodes') -> Dict` | Upload file to Duet
`get_fileinfo(filename: str = None, directory: str = 'gcodes') -> Dict` | Get file info
`delete_file(filename: str, directory: str = 'gcodes') -> Dict` | Delete file on Duet
`move_file(from_path: str, to_path: str, force: bool = False) -> Dict` | Move file on Duet, can be used to rename files
`get_directory(directory: str) -> List[Dict]` | Get a list of all the files & directories in a directory
`create_directory(directory: str) -> Dict` | Create a new directory


## Wrapper
An additional wrapper is provided to make repetative tasks easier

Method | Description
------ | -----------
`emergency_stop() -> None` | Send M112 > M999
`start_print(filename: str) -> Dict` | start a print on duet
`pause_print() -> Dict` | pause current print
`stop_print(leave_heaters: bool) -> Dict` | stop current print, will pause first if not paused
`get_coords() -> Dict` | return the current position of all the movement axes
`get_layer() -> int` | return the current layer number of the print
`get_num_extruders() -> int` | return the number of extruders currently configured
`get_num_tools() -> int` | return the number of tools currently configured
`get_status() -> str` | return the current Duet status
`get_temperature() -> List[Dict]` | return a list of all the analog sensors and their value
`get_current_tool() -> int` | return the current tool number
`get_messagebox() -> Dict` | return the details of a message displayed via `M291` if one exists
`acknowledge_message(response: int) -> Dict` | send an acknowledgement to a message if one exists. Response options are `0` (continue), and `1` (cancel) 
