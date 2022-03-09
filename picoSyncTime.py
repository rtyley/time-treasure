#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
from serial.tools import list_ports
import serial, time
from datetime import timezone
import datetime
from time import gmtime

picoPorts = list(list_ports.grep("2E8A:0005"))
if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    picoSerialPort = picoPorts[0].device
    originalTime = datetime.datetime.now(timezone.utc)
    t = originalTime
    millisToWaitForDeadline = (1000 - (int(t.microsecond/1000) % 1000))
    t.replace(microsecond=0)
    t += datetime.timedelta(seconds=1)

    # year, month, day, hour, minute, second, wday
    print(gmtime())
    timeCube = ",".join(
        [str(x) for x in [t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), millisToWaitForDeadline]])
    print(timeCube)
    with serial.Serial(picoSerialPort) as s:
        # syncMSG = 'T'+str(int(1000*t.timestamp()))
        syncMSG = 'T'+timeCube
        s.write(bytes(syncMSG, "ascii"))
    print( "Raspberry Pi Pico found at "+str(picoSerialPort) )
    print( "Time sync epoch USB MSG: "+syncMSG )
    print( "originalTime: "+str(originalTime) )
    print( "t: "+str(t) )