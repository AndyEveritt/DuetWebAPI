# DuetWebAPI
Python interface to Duet RepRap V3 firmware via Http REST API.

* Works over IP network.
* Does not support passwords on the printer. 
* Supported boards:
  * Duet 3 + SBC
  * Duet 3 standalone
  * Duet 2 standalone

# Install
* add `-e "git+https://github.com/AndyEveritt/DuetWebAPI.git@master#egg=duetwebapi"` to `requirements.txt`
* `pip install -r requirements.txt`

# Usage
* See 'examples.py' for examples. 

## REST API
The REST API allows for the following operations:

Method | Description
------ | -----------
`get_model(key: str = None) -> Dict` | Get Duet object model. RRF3 only
`post_code(code: str) -> Dict` | Send G/M/T-code to Duet
`get_file(filename: str, directory: str = 'gcodes') -> str` | Download file from Duet
`put_file(file: str, directory: str = 'gcodes') -> Dict` | Upload file to Duet
`get_fileinfo(filename: str = None, directory: str = 'gcodes') -> Dict` | Get file info
`delete_file(filename: str, directory: str = 'gcodes') -> Dict` | Delete file on Duet
`move_file(from_path: str, to_path: str, force: bool = False) -> Dict` | Move file on Duet, can be used to rename files
`get_directory(directory: str) -> List[Dict]` | Get a list of all the files & directories in a directory
`put_directory(directory: str) -> Dict` | Create a new directory


## Wrapper
An additional wrapper is provided to make repetative tasks easier

Method | Description
------ | -----------
`get_coords()` | return the current position of all the movement axes
`get_layer()` | return the current layer number of the print
`get_num_extruders()` | return the number of extruders currently configured
`get_num_tools()` | return the number of tools currently configured
`get_status()` | return the current Duet status
`get_temperature()` | return a list of all the analog sensors and their value
