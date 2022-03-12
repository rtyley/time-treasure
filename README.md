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

* Passphrase input: 4x4 keypad with light-up keys labelled with the 8 adjectives and 8 nouns. The KeyBow 2040 is pretty awesome for this.
* Progress indicator: 6 lights that start red, then incrementally turn green with the entry of each correct passphrase
* A sealed door or drawer with a motorised opening mechanism that allows access to the treasure when enough correct passphrases have been entered.





