from sha256 import sha256

# GOOD, BAD, SOGGY, CUTE, SMUG, VILE, NEAT, TIDY, SORE, TINY,
# FROG, LAMB, DEER, GOAT, JOEY, WOLF, MOLE, BEAR, BULL, LION, SEAL

def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value

class Passphrase:
    adjectives = ["GOOD", "BAD" , "FAST", "SLOW", "IRON", "FIRE", "CUTE", "VILE"]
    nouns      = ["BEAR", "DUCK", "FROG", "GOAT", "JOEY", "LAMB", "MOLE", "WOLF"]

    def __init__(self, hashBytes):
        num = reduce(lambda a, b: a ^ b, hashBytes)
        adjectiveIndex = num % len(self.adjectives)
        nounIndex = (num // len(self.adjectives)) % len(self.nouns)
        self.wordIndices = [adjectiveIndex, nounIndex]
        self.words = [Passphrase.adjectives[adjectiveIndex], Passphrase.nouns[nounIndex]]
        self.fullText = ' '.join(self.words)

    def __repr__(self):
        return self.fullText

class TreasurePassphrases:

    def __init__(self, salts):
        self.numSalts = len(salts)
        print(f'numSalts={self.numSalts}')
        self.salts = salts

    def passphraseFor(self, epochSeconds):
        passphraseEpoch = epochSeconds // 1
        # print(f'passphraseEpoch={passphraseEpoch}')
        saltIndex = passphraseEpoch % self.numSalts
        # print(f'saltIndex={saltIndex}')
        salt = self.salts[saltIndex]
        if salt is None:
            return None
        else:
            h = sha256(salt.encode('utf-8'))
            h.update(passphraseEpoch.to_bytes(8,'big'))
            return Passphrase(h.digest())
