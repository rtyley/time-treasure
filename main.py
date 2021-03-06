import time
from machine import Pin
from utime import time, localtime, sleep
from time import ticks_diff, ticks_add, ticks_ms, sleep_us, gmtime
from select import select
from sys import stdin
from machine import SoftI2C

# FROM HERE: https://github.com/peterhinch/micropython-samples/tree/master/DS3231

# ds3231_port.py Portable driver for DS3231 precison real time clock.
# Adapted from WiPy driver at https://github.com/scudderfish/uDS3231

# Author: Peter Hinch
# Copyright Peter Hinch 2018 Released under the MIT license.

import utime
import machine
import sys
DS3231_I2C_ADDR = 104

try:
    picoRTC = machine.RTC()
except:
    print('Warning: machine module does not support the RTC.')
    picoRTC = None

def bcd2dec(bcd):
    return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

def dec2bcd(dec):
    tens, units = divmod(dec, 10)
    return (tens << 4) + units

def tobytes(num):
    return num.to_bytes(1, 'little')

class DS3231:
    def __init__(self, i2c):
        self.ds3231 = i2c
        self.timebuf = bytearray(7)
        if DS3231_I2C_ADDR not in self.ds3231.scan():
            raise RuntimeError("DS3231 not found on I2C bus at %d" % DS3231_I2C_ADDR)

    def get_time(self, set_rtc=False):
        if set_rtc:
            self.await_transition()  # For accuracy set RTC immediately after a seconds transition
        else:
            self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf) # don't wait
        return self.convert(set_rtc)

    def convert(self, set_rtc=False):  # Return a tuple in localtime() format (less yday)
        data = self.timebuf
        ss = bcd2dec(data[0])
        mm = bcd2dec(data[1])
        if data[2] & 0x40:
            hh = bcd2dec(data[2] & 0x1f)
            if data[2] & 0x20:
                hh += 12
        else:
            hh = bcd2dec(data[2])
        wday = data[3]
        DD = bcd2dec(data[4])
        MM = bcd2dec(data[5] & 0x1f)
        YY = bcd2dec(data[6])
        if data[5] & 0x80:
            YY += 2000
        else:
            YY += 1900
        # Time from DS3231 in time.localtime() format (less yday)
        result = YY, MM, DD, hh, mm, ss, wday -1, 0
        if set_rtc:
            if picoRTC is None:
                # Best we can do is to set local time
                secs = utime.mktime(result)
                utime.localtime(secs)
            else:
                picoRTC.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
        return result

    def save_time(self, t):
        (YY, MM, mday, hh, mm, ss, wday, yday) = t
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 0, tobytes(dec2bcd(ss)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 1, tobytes(dec2bcd(mm)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 2, tobytes(dec2bcd(hh)))  # Sets to 24hr mode
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 3, tobytes(dec2bcd(wday + 1)))  # 1 == Monday, 7 == Sunday
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 4, tobytes(dec2bcd(mday)))  # Day of month
        if YY >= 2000:
            self.ds3231.writeto_mem(DS3231_I2C_ADDR, 5, tobytes(dec2bcd(MM) | 0b10000000))  # Century bit
            self.ds3231.writeto_mem(DS3231_I2C_ADDR, 6, tobytes(dec2bcd(YY-2000)))
        else:
            self.ds3231.writeto_mem(DS3231_I2C_ADDR, 5, tobytes(dec2bcd(MM)))
            self.ds3231.writeto_mem(DS3231_I2C_ADDR, 6, tobytes(dec2bcd(YY-1900)))

    # Wait until DS3231 seconds value changes before reading and returning data
    def await_transition(self):
        self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf)
        ss = self.timebuf[0]
        while ss == self.timebuf[0]:
            self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf)
        return self.timebuf

    # Test hardware RTC against DS3231. Default runtime 10 min. Return amount
    # by which DS3231 clock leads RTC in PPM or seconds per year.
    # Precision is achieved by starting and ending the measurement on DS3231
    # one-second boundaries and using ticks_ms() to time the RTC.
    # For a 10-minute measurement +-1ms corresponds to 1.7ppm or 53s/yr. Longer
    # runtimes improve this, but the DS3231 is "only" good for +-2ppm over 0-40C.
    def rtc_test(self, runtime=600, ppm=False, verbose=True):
        if picoRTC is None:
            raise RuntimeError('machine.RTC does not exist')
        verbose and print('Waiting {} minutes for result'.format(runtime//60))
        factor = 1_000_000 if ppm else 114_155_200  # seconds per year

        self.await_transition()  # Start on transition of DS3231. Record time in .timebuf
        t = utime.ticks_ms()  # Get system time now
        ss = picoRTC.datetime()[6]  # Seconds from system RTC
        while ss == picoRTC.datetime()[6]:
            pass
        ds = utime.ticks_diff(utime.ticks_ms(), t)  # ms to transition of RTC
        ds3231_start = utime.mktime(self.convert())  # Time when transition occurred
        t = picoRTC.datetime()
        rtc_start = utime.mktime((t[0], t[1], t[2], t[4], t[5], t[6], t[3] - 1, 0))  # y m d h m s wday 0

        utime.sleep(runtime)  # Wait a while (precision doesn't matter)

        self.await_transition()  # of DS3231 and record the time
        t = utime.ticks_ms()  # and get system time now
        ss = picoRTC.datetime()[6]  # Seconds from system RTC
        while ss == picoRTC.datetime()[6]:
            pass
        de = utime.ticks_diff(utime.ticks_ms(), t)  # ms to transition of RTC
        ds3231_end = utime.mktime(self.convert())  # Time when transition occurred
        t = picoRTC.datetime()
        rtc_end = utime.mktime((t[0], t[1], t[2], t[4], t[5], t[6], t[3] - 1, 0))  # y m d h m s wday 0

        d_rtc = 1000 * (rtc_end - rtc_start) + de - ds  # ms recorded by RTC
        d_ds3231 = 1000 * (ds3231_end - ds3231_start)  # ms recorded by DS3231
        ratio = (d_ds3231 - d_rtc) / d_ds3231
        ppm = ratio * 1_000_000
        verbose and print('DS3231 leads RTC by {:4.1f}ppm {:4.1f}mins/yr'.format(ppm, ppm*1.903))
        return ratio * factor

    def _twos_complement(self, input_value: int, num_bits: int) -> int:
        mask = 2 ** (num_bits - 1)
        return -(input_value & mask) + (input_value & ~mask)

    def get_temperature(self):
        t = self.ds3231.readfrom_mem(DS3231_I2C_ADDR, 0x11, 2)
        i = t[0] << 8 | t[1]
        return self._twos_complement(i >> 6, 10) * 0.25

# from ds3231_port import DS3231

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class RTC:
    def __init__(self):
        rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=100000)
        self.ds = DS3231(rtc_i2c)
        pass

    def get_time(self):
        return self.ds.get_time()

    def save_time(self, t):
        return self.ds.save_time(t)

# Write your code here :-)
picoRTC = machine.RTC()
print(picoRTC.datetime())
print(RTC().get_time())
# (2022, 3, 9,  3, 20, 52, 30, 0)
# (1922, 3, 9, 20, 52,  7,  2, 0)

def readDeadlineAndTimeToDeadlineFromUSB():
    ch, buffer = '',''
    ticks_ms_for_read_instant = ticks_ms()
    while stdin in select([stdin], [], [], 0)[0]:
        ch = stdin.read(1)
        buffer = buffer+ch
    if buffer:
        print("Received USB data!")
        for i in range(len(buffer)):
            if buffer[i] == 'T':
                break
        buffer = buffer[i:]
        if buffer[:1] == 'T' and buffer[-1] == '_':
            buffData = buffer[1:-1]
            buffFields = [int(x) for x in buffData.split(',')]
            deadLineFields = buffFields[:-1]
            deadLineFields.append(0)
            timeToDeadLine = buffFields[-1]
            print("timeToDeadLine:",end='');print(timeToDeadLine)
            return deadLineFields, ticks_add(ticks_ms_for_read_instant, timeToDeadLine)

led_onboard = Pin(25, Pin.OUT)

picoRTC = machine.RTC()
lastSecondPrinted = picoRTC.datetime()[6]

while True:
    picoTime=picoRTC.datetime()
    ds3231Time = RTC().get_time()
    secondsFromPico = picoTime[6]
    secondsFromDS3231Time = ds3231Time[5]
    if secondsFromPico != lastSecondPrinted:
        picoTime=picoRTC.datetime()
        print('Pico   RTC :',end='');print(picoTime)
        print('DS3231 RTC :',end='');print(ds3231Time)
        print('Pico   seconds :',end='');print(secondsFromPico)
        print('DS3231 seconds :',end='');print(secondsFromDS3231Time)
        lastSecondPrinted = secondsFromPico
        led_onboard.toggle()

    receivedTimeDataFromUsb = readDeadlineAndTimeToDeadlineFromUSB()
    if receivedTimeDataFromUsb:
        deadLineFields, deadline_ticks = receivedTimeDataFromUsb
        print("deadLineFields: ",end='');print(deadLineFields)
        (year, month, day, hour, minute, second, wday, yday) = deadLineFields
        while ticks_diff(deadline_ticks, ticks_ms()) > 0:
            sleep_us(1000)  # *ticks_diff(deadline, time.ticks_ms())
        RTC().save_time(deadLineFields)
        picoRTC.datetime((year, month, day, wday, hour, minute, second, 0))
        print("Saved time from USB\t: ",end='');print(deadLineFields)
        print("PICO RTC says\t:",end='');print(picoRTC.datetime())
        print("DS3231 now says\t:",end='');print(RTC().get_time())


