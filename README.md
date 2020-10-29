# DuetWebAPI
Python interface to Duet RepRap V2 or V3 firmware via Http REST API. 

* Works over IP network.  
* Does not support passwords on the printer. 
* Abstracts V2 to V3 differences. 
* NOT a general purpose interace; instead it has
  specific methods to issue commands or return
  information.  Adding new methods is encouraged,
  as long as they continue V2 V3 abstractaion.

# Install
* add `"git+https://github.com/AndyEveritt/DuetWebAPI.git@master#egg=duetwebapi"` to `requirements.txt`
* `pip install -r requirements.txt`

# Usage
* See 'examples.py' for examples. 
