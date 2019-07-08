from PyQt5.QtCore import QObject
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QAbstractSocket

from settings.netSettings import NetSettings


class _OutcomingConnection:
    def __init__(self):
        self.socketDescriptor = 0
        self.socket = None
        self.remoteAddress = ""
        self.remotePort = 0
        self.connected = False
        self.dataPackets = list()


class ResenderEngine(QObject):
    def __init__(self, parent=None, port=NetSettings.nodeDataPort):
        super().__init__(parent)
        self.__outcomingConnections = dict()  # QMap<QString, OutcomingConnection>
        self.__remoteAddresses = list() # Ip's
        self.__hostAddress = '127.0.0.1'  # address to omit
        self.__remotePort = port

    def __del__(self):
        pass
        # self.stop()

    @pyqtSlot(list)
    def setRemoteAddresses(self, addressList: list):
        self.stop()
        #print(addressList, "SET ADDDRESES")
        self.__remoteAddresses = addressList

    @pyqtSlot(str)
    def setHostAddress(self, address: str):
        self.__hostAddress = address

    @pyqtSlot()
    def stop(self):
        for outcomingConnection in self.__outcomingConnections.values():
            # outcomingConnection.socket.connected.disconnect()
            # outcomingConnection.socket.disconnected.disconnect()
            # outcomingConnection.socket.error.disconnect()
            if outcomingConnection.connected:
                outcomingConnection.socket.disconnectFromHost()
        self.__outcomingConnections.clear()

    @pyqtSlot(str, str)
    def floodPacket(self, packet: str, addressToOmit=str()):
        for address in self.__remoteAddresses:
            #print("FLOOD", address, self.__hostAddress, addressToOmit)
            if not len(address):
                return
            if address != addressToOmit and address != self.__hostAddress:
                self.sendPacket(address, packet)

    @pyqtSlot(str, str)
    def sendPacket(self, address: str, packet: str):
        #print("SEND_PACKET:", address, packet)
        if not address:
            return
        outcomingConnection = self.__outcomingConnections.get(address, None)
        if not outcomingConnection:
            print("NO IN OUTCOME", address, len(address))
            outcomingConnection = _OutcomingConnection()
            outcomingConnection.dataPackets.append(packet.encode())
            outcomingConnection.socket = QTcpSocket(self)
            outcomingConnection.socket.setSocketOption(QAbstractSocket.LowDelayOption, 1)
            outcomingConnection.socket.setSocketOption(QAbstractSocket.KeepAliveOption, 0)
            outcomingConnection.socket.setObjectName(address)
            outcomingConnection.socket.connected.connect(self.__newConnection)
            outcomingConnection.socket.disconnected.connect(self.__disconnected)
            outcomingConnection.socket.error.connect(self.__error)
            outcomingConnection.remoteAddress = address
            outcomingConnection.remotePort = self.__remotePort
            outcomingConnection.socket.connectToHost(address, self.__remotePort)

            self.__outcomingConnections[address] = outcomingConnection
            #print("STARTED CON")
        else:
            if outcomingConnection.socket.state() == QAbstractSocket.ConnectedState:
                outcomingConnection.dataPackets.append(packet.encode())
                self._sendPackets(outcomingConnection)
            else:
                if outcomingConnection.socket.state() != QAbstractSocket.ConnectingState:
                    outcomingConnection.socket.disconnectFromHost()
                    outcomingConnection.socket.connectToHost(outcomingConnection.remoteAddress, self.__remotePort)

    @pyqtSlot()
    def __newConnection(self):
        #print("NEW CONNECT TO")
        socket = self.sender()
        outcomingConnection = self.__outcomingConnections[socket.peerAddress().toString()]
        # outcomingConnection.socketDescriptor = socket.socketDescriptor()
        outcomingConnection.connected = True
        socket.disconnected.connect(self.__disconnected)
        self._sendPackets(outcomingConnection)

    def _sendPackets(self, outcomingConnection: _OutcomingConnection):
        #print("SEND PACKET 2")
        if outcomingConnection.socket.state() == QAbstractSocket.ConnectedState:
            #print("SEND PACKET 2 2")
            packets = outcomingConnection.dataPackets
            for packet in packets:
                packetLength = len(packet)
                bytesWritten = 0
                while bytesWritten != 4:
                    bytesWritten += outcomingConnection.socket.writeData(packetLength.to_bytes(4, byteorder="little"))
                bytesWritten = 0
                while bytesWritten != packetLength:
                    bytesWritten += outcomingConnection.socket.writeData(packet)
                outcomingConnection.socket.flush()
            outcomingConnection.dataPackets.clear()

    @pyqtSlot()
    def __disconnected(self):
        socket = self.sender()
        outcomingConnection = self.__outcomingConnections.get(socket.objectName(), None)
        if outcomingConnection:
            outcomingConnection.connected = False
            outcomingConnection.dataPackets.clear()
            # outcomingConnection.commandPackets.clear()
            # outcomingConnection.dSocket.disconnected.disconnect()
            # outcomingConnection.cSocket.disconnected.disconnect()

    @pyqtSlot()
    def __error(self):
        socket = self.sender()
        print("ERROR", socket.errorString(), socket.objectName(), socket.peerAddress().toString())
