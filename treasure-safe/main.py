# SPDX-FileCopyrightText: 2021 Sandy Macdonald
#
# SPDX-License-Identifier: MIT

# A simple example of how to set up a keymap and HID keyboard on Keybow 2040.

# You'll need to connect Keybow 2040 to a computer, as you would with a regular
# USB keyboard.

# Drop the keybow2040.py file into your `lib` folder on your `CIRCUITPY` drive.

# NOTE! Requires the adafruit_hid CircuitPython library also!

import board
from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
# from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base

import adafruit_ds3231
import rtc
import time
from supervisor import ticks_ms
from select import select
from sys import stdin
import random

from passphrases import TreasurePassphrases

treasurePassphrases = TreasurePassphrases([
    "Freedom-Pattern-Drum-Origin-2",
    "Zoo-Child-Century-Weave-Faint-1"
])


# Set up Keybow
hardware = Hardware()
i2c = hardware.i2c()

batteryRTC = adafruit_ds3231.DS3231(i2c)


_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

def ticks_add(ticks, delta):
    "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (a + b) % _TICKS_PERIOD

def ticks_diff(ticks1, ticks2):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff

def ticks_less(ticks1, ticks2):
    "Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks"
    return ticks_diff(ticks1, ticks2) < 0









keybow = PMK(hardware)
keys = keybow.keys




# pylint: disable-msg=using-constant-test
if False:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2022, 03, 28, 14, 30, 30, 0, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print("Setting time to:", t)  # uncomment for debugging
    batteryRTC.datetime = t
    print()

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
t = batteryRTC.datetime
print(t)     # uncomment for debugging
print(
    "The date is {} {}/{}/{}".format(
        days[int(t.tm_wday)], t.tm_mday, t.tm_mon, t.tm_year
    )
)
print("The time is {}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))




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

picoRTC = rtc.RTC()
lastSecondPrinted = picoRTC.datetime.tm_sec

while False:
    picoTime=picoRTC.datetime
    ds3231Time = batteryRTC.datetime
    secondsFromPico = picoTime.tm_sec
    secondsFromDS3231Time = ds3231Time.tm_sec
    if secondsFromPico != lastSecondPrinted:
        print('Pico   RTC :',end='');print(picoTime)
        print('DS3231 RTC :',end='');print(ds3231Time)
        print('Pico   seconds :',end='');print(secondsFromPico)
        print('DS3231 seconds :',end='');print(secondsFromDS3231Time)
        lastSecondPrinted = secondsFromPico

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



# Write your code here :-)
import board
import digitalio
import adafruit_aw9523
from time import sleep

aw = adafruit_aw9523.AW9523(i2c)
aw.directions = 0xFFFF
print(aw.LED_modes)



windowPinNumbers = [1,2,3,4] # [1,2,3,4,5,6,7,12]

aw.LED_modes = 0x0000
#aw.LED_modes = 0xFFFF

for windowPinNum in windowPinNumbers:
    windowPin = aw.get_pin(windowPinNum)
    windowPin.switch_to_output(value=True)
    aw.set_constant_current(windowPinNum, 255)

print(aw.LED_modes)

keyNumByWord = {
    "GOOD" : 12,
    "BAD" : 8,
    "FAST" : 13,
    "SLOW" : 9,
    "IRON" : 14,
    "FIRE" : 10,
    "CUTE" : 15,
    "VILE" : 11,
    "BEAR" : 4,
    "DUCK" : 0,
    "FROG" : 5,
    "GOAT" : 1,
    "JOEY" : 6,
    "LAMB" : 2,
    "MOLE" : 7,
    "WOLF" : 3
}

wordByKeyNum = {v: k for k, v in keyNumByWord.items()}


# The colour to set the keys when pressed
rgb = (255, 255, 0)


# Attach handler functions to all of the keys
for key in keys:
    # key.set_led(*rgb)

    # A press handler that sends the keycode and turns on the LED
    @keybow.on_press(key)
    def press_handler(key):
        print(key.number)
        print(wordByKeyNum[key.number])
        # keycode = keymap[key.number]
        key.set_led(*rgb)
        windowPinNum = random.choice(windowPinNumbers)
        windowPin = aw.get_pin(windowPinNum)
        # aw.set_constant_current(windowPinNum, random.randint(0, 256))
        # windowPin.value = 1 - windowPin.value
        # aw.set_constant_current(windowPin, 255)

    # A release handler that turns off the LED
    @keybow.on_release(key)
    def release_handler(key):
        key.led_off()
        # key.set_led(*(255, 255, 255))

# aw.LED_modes = 0xFFFF
# n = 0
# while True:
#    for pin in range(16):
#        # every LED is 'offset' by 16 counts so they dont all pulse together
#        aw.set_constant_current(pin, (pin * 16 + n) % 256)
#    # n increments to increase the current from 0 to 255, then wraps around
#    n = (n + 1) % 256

score = 0
lastCorrectPassPhrase = None
while True:
    # Always remember to call keybow.update()!
    keybow.update()
    #print(t)     # uncomment for debugging
    t = batteryRTC.datetime
    #print("The time is {}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
    passphrase = treasurePassphrases.passphraseFor((t.tm_min*60) + t.tm_sec)
    # print(f'passphrase = {treasurePassphrases.passphraseFor((t.tm_min*60) + t.tm_sec)}')

    if lastCorrectPassPhrase != passphrase.fullText and set(keybow.get_pressed()) == set([keyNumByWord[word] for word in passphrase.words]):
        lastCorrectPassPhrase = passphrase.fullText
        print(f'Score {score}')
        score = score + 1

    # for word in passphrase.words:
    #    keys[keyNumByWord[word]].set_led(*rgb)

    happyPins = windowPinNumbers[:score]
    print(happyPins)

    for pin in windowPinNumbers[:score]:
        windowPin = aw.get_pin(pin)
        windowPin.value = 0

while True:
    for pin in windowPins:
        sleep(0.5)
        pin.value = 0


    sleep(2)
    for pin in windowPins:
        pin.value = 1
