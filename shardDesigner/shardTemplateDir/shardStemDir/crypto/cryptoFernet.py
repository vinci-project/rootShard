from cryptography.fernet import Fernet
from crypto.mrkl import VncTree
import base64

class cryptoFernet():
    def __init__(self, password):
        self.cipher_key = base64.urlsafe_b64encode(VncTree.hash(password)[0:32].encode())


    def crypt(self, data: str):
        cipher = Fernet(self.cipher_key)
        cryptData = cipher.encrypt(data.encode())
        return cryptData

    def decrypt(self, data: bytes):
        cipher = Fernet(self.cipher_key)
        decryptData = cipher.decrypt(data)
        return decryptData




