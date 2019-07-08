from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from . import receiver
from . import resender

from settings.netSettings import NetSettings


class NetEngine(QObject):
    # signals for ReceiverEngine
    runReceiver = pyqtSignal(str)
    setMaxPendingConnections = pyqtSignal(int)
    stopReceiver = pyqtSignal()
    newDataPacket = pyqtSignal(str, str)
    # signals for ResenderEngine
    setRemoteAddresses = pyqtSignal(list)
    floodPacketSignal = pyqtSignal(str, str, int)
    sendPacketSignal = pyqtSignal(str, str, int)

    floodDataPacket = pyqtSignal(str, str)
    sendDataPacket = pyqtSignal(str, str)

    floodCommandPacket = pyqtSignal(str, str)
    sendCommandPacket = pyqtSignal(str, str)

    stopResender = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        #self.__dataReceiver = receiver.ReceiverEngine(None, NetSettings.nodeDataPort)
        #self.__dataResender = resender.ResenderEngine(None, NetSettings.nodeDataPort)

        self.__commandReceiver = receiver.ReceiverEngine(self, NetSettings.nodeCommandPort)
        self.__commandResender = resender.ResenderEngine(self, NetSettings.nodeCommandPort)

        self.__receiverThread = QThread(self)
        self.__resenderThread = QThread(self)

        #self.__dataReceiver.moveToThread(self.__receiverThread)
        #self.__dataResender.moveToThread(self.__resenderThread)

        self.floodPacketSignal.connect(self.floodPacketSlot)
        self.sendPacketSignal.connect(self.sendPacketSlot)

        # Receivers connections

        #self.runReceiver.connect(self.__dataReceiver.runReceiver)
        #self.setMaxPendingConnections.connect(self.__dataReceiver.setMaxPendingConnections)
        #self.stopReceiver.connect(self.__dataReceiver.stop)
        #self.__dataReceiver.newDataPacket.connect(self.newDataPacket)

        self.runReceiver.connect(self.__commandReceiver.runReceiver)
        self.setMaxPendingConnections.connect(self.__commandReceiver.setMaxPendingConnections)
        self.stopReceiver.connect(self.__commandReceiver.stop)
        self.__commandReceiver.newDataPacket.connect(self.newDataPacket)

        # Resenders connections

        #self.setRemoteAddresses.connect(self.__dataResender.setRemoteAddresses)
        #self.floodDataPacket.connect(self.__dataResender.floodPacket)
        #self.sendDataPacket.connect(self.__dataResender.sendPacket)
        #self.stopResender.connect(self.__dataResender.stop)
        #self.runReceiver.connect(self.__dataResender.setHostAddress)

        self.setRemoteAddresses.connect(self.__commandResender.setRemoteAddresses)
        self.floodCommandPacket.connect(self.__commandResender.floodPacket)
        self.sendCommandPacket.connect(self.__commandResender.sendPacket)
        self.stopResender.connect(self.__commandResender.stop)
        self.runReceiver.connect(self.__commandResender.setHostAddress)

        #self.__receiverThread.finished.connect(self.__dataReceiver.deleteLater)
        #self.__resenderThread.finished.connect(self.__dataResender.deleteLater)

        self.__receiverThread.start()
        self.__resenderThread.start()

    @pyqtSlot()
    def onAboutToQuit(self):
        #self.__dataReceiver.newDataPacket.disconnect(self.newDataPacket)

        self.stopReceiver.emit()
        self.stopResender.emit()

        self.__receiverThread.quit()
        self.__resenderThread.quit()
        self.__receiverThread.wait()
        self.__resenderThread.wait()

    @pyqtSlot(str, str, int)
    def floodPacketSlot(self, packet: str, addressToOmit=str(), priority=0):
        if priority:
            self.floodCommandPacket.emit(packet, addressToOmit)
        else:
            self.floodDataPacket.emit(packet, addressToOmit)

    @pyqtSlot(str, str, int)
    def sendPacketSlot(self, address: str, packet: str, priority=0):
        if priority:
            self.sendCommandPacket.emit(address, packet)
        else:
            self.sendDataPacket.emit(address, packet)




