from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
import json

from crypto.vncCrypto import VncCrypto


class SignChecker(QObject):
    validTran = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__cryptor = VncCrypto()

    @pyqtSlot(str, str)
    def checkTran(self, address, packet):
        try:
            jsonPacket = json.loads(packet)
        except json.JSONDecodeError:
            print("WRONG JSON PACKET, IN CHECKTRAN WITH 2 ARG")
            return False
        signature = jsonPacket.pop("SIGNATURE", None)
        sender = jsonPacket.get("SENDER", None)
        if signature and sender:

            print("ПРОВЕРЯЮ БЛОК:", json.dumps(jsonPacket, separators=(',', ':')))
            print("ПОДПИСЬ:", signature)
            print("КЛЮЧ:", sender)

            if self.__cryptor.verifyMessage(signature, sender, json.dumps(jsonPacket, separators=(',', ':'))):
                self.validTran.emit(address, packet)
                return True
            else:
                print("WRONG SIGNATURE", self.__cryptor.getLastError())
                return False

    def checkTran(self, packet):
        try:
            jsonPacket = json.loads(packet)
        except json.JSONDecodeError:
            print("WRONG JSON PACKET, IN CHECKTRAN WITH 1 ARG")
            return False
        signature = jsonPacket.pop("SIGNATURE", None)
        sender = jsonPacket.get("SENDER", None)
        if signature and sender:

            if self.__cryptor.verifyMessage(signature, sender, json.dumps(jsonPacket, separators=(',', ':'))):
                return True
            else:
                print("WRONG SIGNATURE", self.__cryptor.getLastError())
                return False
