class OldDuetWebAPI:

    pt = 0


####
# The following methods are a more atomic, reading/writing basic data structures in the printer.
####


    def printerType(self):
        return(self.pt)

    def baseURL(self):
        return(self._base_url)



    def getCoords(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc = j['coords']['xyz']
            an = j['axisNames']
            ret = self.json.loads('{}')
            for i in range(0, len(jc)):
                ret[an[i]] = jc[i]
            return(ret)
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            ja = j['result']['move']['axes']
            # d=j['result']['move']['drives']
            # ad=self.json.loads('{}')
            # for i in range(0,len(ja)):
            #    ad[ ja[i]['letter'] ] = ja[i]['drives'][0]
            ret = self.json.loads('{}')
            for i in range(0, len(ja)):
                ret[ja[i]['letter']] = ja[i]['userPosition']
            return(ret)

    def getLayer(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=3')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            s = j['currentLayer']
            return (s)
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            s = j['result']['job']['layer']
            if (s == None):
                s = 0
            return(s)

    def getG10ToolOffset(self, tool):
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            ja = j['result']['move']['axes']
            jt = j['result']['tools']
            ret = self.json.loads('{}')
            to = jt[tool]['offsets']
            for i in range(0, len(to)):
                ret[ja[i]['letter']] = to[i]
            return(ret)
        return({'X': 0, 'Y': 0, 'Z': 0})      # Dummy for now

    def getNumExtruders(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc = j['coords']['extr']
            return(len(jc))
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(len(j['result']['move']['extruders']))

    def getNumTools(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc = j['tools']
            return(len(jc))
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(len(j['result']['tools']))

    def getStatus(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            s = j['status']
            if ('I' in s):
                return('idle')
            if ('P' in s):
                return('processing')
            if ('S' in s):
                return('paused')
            if ('B' in s):
                return('canceling')
            return(s)
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(j['result']['state']['status'])

    # def gCode(self, command):
    #     if (self.pt == 2):
    #         URL = (f'{self._base_url}'+'/rr_gcode?gcode='+command)
    #         r = self.requests.get(URL)
    #     if (self.pt == 3):
    #         URL = (f'{self._base_url}'+'/machine/code/')
    #         r = self.requests.post(URL, data=command)
    #     if (r.ok):
    #         return(0)
    #     else:
    #         print("gCode command return code = ", r.status_code)
    #         print(r.reason)
    #         return(r.status_code)

    # def getFilenamed(self, filename):
    #     if (self.pt == 2):
    #         URL = (f'{self._base_url}'+'/rr_download?name='+filename)
    #     if (self.pt == 3):
    #         URL = (f'{self._base_url}'+'/machine/file/'+filename)
    #     r = self.requests.get(URL)
    #     return(r.text.splitlines())  # replace('\n',str(chr(0x0a))).replace('\t','    '))

    # def getDirectory(self, directory):
    #     if (self.pt == 2):
    #         URL = (f'{self._base_url}'+'/rr_download?name='+directory)
    #     if (self.pt == 3):
    #         URL = (f'{self._base_url}'+'/machine/directory/'+directory)
    #     r = self.requests.get(URL)
    #     return(r.text.splitlines())  # replace('\n',str(chr(0x0a))).replace('\t','    '))

    def putFile(self, filepath, file):

        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_upload?name='+filepath)  # lol, probably not correct, fix welcome
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/file/'+filepath)
        r = self.requests.put(URL, data=file)
        if (r.ok):
            return(0)
        else:
            print("gCode command return code = ", r.status_code)
            print(r.reason)

    def getTemperatures(self):
        if (self.pt == 2):
            URL = (f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return('Error: getTemperatures not implemented (yet) for RRF V2 printers.')
        if (self.pt == 3):
            URL = (f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jsa = j['result']['sensors']['analog']
            return(jsa)


####
# The following methods provide services built on the atomics above.
####

    # Given a line from config g that defines an endstop (N574) or Z probe (M558),
    # Return a line that will define the same thing to a "nil" pin, i.e. undefine it


    def _nilEndstop(self, configLine):
        ret = ''
        for each in [word for word in configLine.split()]:
            ret = ret + (each if (not (('P' in each[0]) or ('p' in each[0]))) else 'P"nil"') + ' '
        return(ret)

    def clearEndstops(self):
        c = self.getFilenamed('/sys/config.g')
        for each in [line for line in c if (('M574 ' in line) or ('M558 ' in line))]:
            self.gCode(self._nilEndstop(each))

    def resetEndstops(self):
        c = self.getFilenamed('/sys/config.g')
        for each in [line for line in c if (('M574 ' in line) or ('M558 ' in line))]:
            self.gCode(self._nilEndstop(each))
        for each in [line for line in c if (('M574 ' in line) or ('M558 ' in line) or ('G31 ' in line))]:
            self.gCode(each)

    def resetAxisLimits(self):
        c = self.getFilenamed('/sys/config.g')
        for each in [line for line in c if 'M208 ' in line]:
            self.gCode(each)

    def resetG10(self):
        c = self.getFilenamed('/sys/config.g')
        for each in [line for line in c if 'G10 ' in line]:
            self.gCode(each)

    def yeetJob(self, filename, file):
        path = f"gcodes/{filename}"
        ret = self.putFile(path, file)
        if ret == 0:
            print('YAY WE DID THE THING')
