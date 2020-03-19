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

class DuetWebAPI:
    import requests
    import json
    import sys
    pt = 0
    _base_url = ''

    def __init__(self,base_url):
        self._base_url = base_url
        try:
            URL=(f'{self._base_url}'+'/rr_status?type=1')
            r = self.requests.get(URL,timeout=(2,60))
            j = self.json.loads(r.text)
            _=j['coords']
            self.pt = 2
            return
        except:
            try:
                URL=(f'{self._base_url}'+'/machine/status')
                r = self.requests.get(URL,timeout=(2,60))
                j = self.json.loads(r.text)
                _=j['result']
                self.pt = 3
                return
            except:
                print(self._base_url," does not appear to be a RRF2 or RRF3 printer", file=self.sys.stderr)
                return 

    def printerType(self):
        return(self.pt)

    def baseURL(self):
        return(self._base_url)

    def getCoords(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc=j['coords']['xyz']
            an=j['axisNames']
            ret=self.json.loads('{}')
            for i in range(0,len(jc)):
                ret[ an[i] ] = jc[i]
            return(ret)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            ja=j['result']['move']['axes']
            jd=j['result']['move']['drives']
            ad=self.json.loads('{}')
            for i in range(0,len(ja)):
                ad[ ja[i]['letter'] ] = ja[i]['drives'][0]
            ret=self.json.loads('{}')
            for i in range(0,len(ja)):
                ret[ ja[i]['letter'] ] = jd[i]['position']
            return(ret)

    def getNumExtruders(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc=j['coords']['xyz']
            an=j['axisNames']
            ret=self.json.loads('{}')
            for i in range(0,len(jc)):
                ret[ an[i] ] = jc[i]
            return(ret)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(len(j['result']['tools']))

    def gCode(self,command):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_gcode?gcode='+command)
            r = self.requests.get(URL)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/code/')
            r = self.requests.post(URL, data=command)
        if (r.ok):
           return(0)
        else:
            print("gCode command return code = ",r.status_code)
            print(r.reason)
            return(r.status_code)
