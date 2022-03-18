# treasure-clock

## Devices

* **Treasure Safe**, with passphrase entry keypad, status lights, and opening mechanism
* **Passphrase Displays** (x2)

Both kinds of device need to:

* Have independent battery power, as there are no electrical power supplies in the park!
* Have an accurate Real Time Clock (RTC), so they can agree what the current one-time passphrase is.
* Be securable (immovable), ie by zip-tie attachment to a tree branch
* Not worry people who see them. Should prominently display the date of the treasure hunt in static lettering, and ideally indicate that they will be removed quickly the same day, soon after the treasure hunt completes. Hopefully not look like any kind of commercial operation.

### One-time passphrases

Current passphrase can be calculated as follows:

```
adjectives = ["Good", "Bad" , "Cute", "Vile", ...]
nouns      = ["Duck", "Goat", "Frog", "Lamb", ...]

passphraseEpoch = int(epochSeconds / 10)
passphraseSalt = salts[passphraseEpoch % salts.size]
passphraseNumber = sha256(passphraseEpoch ++ passphraseSalt).last6bits
passphraseWord1 = adjectives[passphraseNumber.first3bits]
passphraseWord2 = nouns[passphraseNumber.last3bits]
```

This requires accesss to SHA256, which hopefully is supported everywhere:

* https://docs.micropython.org/en/latest/library/hashlib.html
* https://docs.circuitpython.org/en/latest/docs/library/hashlib.html


### Treasure Safe

The Treasure Safe contains treasure, but will only release it when a correct sequence of 6 one-time passphrases has been entered.

#### External interface exposed by Treasure Safe

* Passphrase input: 4x4 keypad with light-up keys labelled with the 8 adjectives and 8 nouns. Should be positioned so that children can easily read the labels on the keys and enter passphrases. The [KeyBow 2040](https://shop.pimoroni.com/products/keybow-2040?variant=32399559589971)
  is pretty awesome for this.
* Progress indicator: 6 lights that start red, then incrementally turn green with the entry of each correct passphrase
* A sealed door or drawer with a motorised opening mechanism that allows access to the treasure when enough correct passphrases have been entered.

#### Construction of Treasure Safe

The container and the mechanism mostly implemented in Lego. It must be possible to secure this to a tree branch so that the device can not be moved. It may be necessary to enclose the device in a partial case if Lego is too delicate/easy to disassemble.

The Keypad should be mounted securely on the surface of the safe.

#### Electronic components

* KeyBow 2040
* Adafruit AW9523 GPIO Expander and LED Driver Breakout - STEMMA QT / Qwiic
  ([guide](https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver/python-circuitpython), [Circuitpython](https://github.com/adafruit/Adafruit_CircuitPython_AW9523))
* Adafruit DS3231 Precision RTC - STEMMA QT
* Flexible RGB LED Strip - DotStar - 6 LEDs -- assuming we can drive this from the GPIO expander.
* LED - Infrared - 940nm
* Transistor (to drive IR LED) - connected to GPIO 0, the TX pin?
* Linear motion limit sensors
* Lego power functions sensor(s!?), battery box, and motor(s?)
