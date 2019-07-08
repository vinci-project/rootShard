import hashlib
import coincurve


def blake2b(bytestr: bytes) -> bytes:
    return hashlib.blake2b(bytestr, digest_size=32).digest()


class VncCrypto:
    lastError = str()

    def __init__(self):
        self.__privateKey = None
        self.__lastError = str()

    def setPrivateKey(self, privateKey: str) -> bool:
        if not privateKey:
            self.generateKeys()
            return True
        elif len(privateKey) != 64:
            self.__lastError = "VALUE ERROR. BAD DATA."
            return False
        else:
            self.__privateKey = coincurve.PrivateKey.from_hex(privateKey)
            return True

    def generateKeys(self) -> str:
        self.__privateKey = coincurve.PrivateKey()

    def getPublicKey(self) -> str:
        return self.__privateKey.public_key.format(True).hex()

    def getPrivateKey(self) -> str:
        return self.__privateKey.to_hex()

    def signMessage(self, msg: str) -> str:
        return self.__privateKey.sign_recoverable(msg.encode(), hasher=blake2b).hex()

    def verifyMessage(self, signature: str, publicKey: str, msg: str) -> bool:
        restoredPublicKey = coincurve.PublicKey.from_signature_and_message(bytes.fromhex(signature),
                                                                           msg.encode(),
                                                                           hasher=blake2b).format(True).hex()
        return restoredPublicKey == publicKey

    def getLastError(self):
        return self.__lastError