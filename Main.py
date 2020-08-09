#!/usr/bin/env python3
import DuetWebAPI as DWA
import json

# Test cases

SBB = DWA.DuetWebAPI('http://192.168.0.164')
Mongo = DWA.DuetWebAPI('http://192.168.0.186')

def tempparse(machine):
    numextruders=machine.getNumExtruders
    tempdict=machine.getTemperatures()
    #print(type(tempdict))
    
    heaters={}
    for i,value in enumerate(tempdict):
        #print(value['state'])
        #print(type(value['state']))
        heaters[i]={'state':value['state'], 'activetemp':value['active'], 'standbytemp':value['standby'], 'currenttemp':value['current']}
        print(heaters)
    return (heaters)

#def heaterfraction(heaterdata):
    #for key in heaterdata:
        #if 



#print("Printer Type SBB is ",SBB.printerType())


#print("SBB coordinates are",SBB.getCoords())

#print("SBB numExtruders ",SBB.getNumExtruders())


#print("SBB numTools ",SBB.getNumTools())
print("SBB Status is...",SBB.getStatus())
#print("SBB length of config.g ",len(SBB.getFilenamed('/sys/config.g')))
#print("SBB TempTools ",SBB.getTemperatures())
heatersinfo=tempparse(SBB)
print("mongo",Mongo.getJob())
print("stablebot", SBB.getJob())




