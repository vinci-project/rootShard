from PyQt5.QtCore import QObject
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtNetwork import QTcpServer
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtNetwork import QHostAddress

from crypto.signChecker import SignChecker
from settings.netSettings import NetSettings


class _IncomingConnection:
    def __init__(self):
        self.receivingPacketSize = 0
        self.socketDescriptor = 0
        self.socket = None
        self.buffer = None
        self.address = ""
        self.port = 0


class ReceiverEngine(QObject):
    newDataPacket = pyqtSignal(str, str)

    def __init__(self, parent=None, port=NetSettings.nodeDataPort):
        super().__init__(parent)
        self.__incomingConnections = dict() # QMap<QTcpSocket*, _IncomingConnection>
        self.__incomingConnectionsAddress = str()
        self.__incomingConnectionsPort = int()
        self.__server = None
        self.__signChecker = SignChecker()
        self.__serverPort = port

    def __del__(self):
        pass
        # self.stop()

    @pyqtSlot()
    def setMaxPendingConnections(self, numConnections: int):
        if not self.__server:
            return
        self.__server.setMapPendingConnections(numConnections)

    def isListening(self):
        if not self.__server:
            return False
        # SHOULD BE PROTECTED WITH MUTEX
        return self.__server.isListening()

    @pyqtSlot(str)
    def runReceiver(self, hostAddress: str):
        if not self.__server:
            self.__server = QTcpServer(self)
            self.__server.acceptError.connect(self.__error)
        if not self.__server.listen(QHostAddress(hostAddress), self.__serverPort) and not self.isListening():
            print("RECEIVER NOT STARTED", self.__server.errorString())
        else:
            self.__server.newConnection.connect(self.__newConnection)
            self.__incomingConnectionsAddress = hostAddress
            self.__incomingConnectionsPort = self.__serverPort
            print("RECEIVER STARTED")

    @pyqtSlot()
    def stop(self):
        if not self.__server:
            return
        if self.isListening():
            for socket in self.__incomingConnections.keys():
                socket.readyRead.disconnect()
                socket.disconnected.disconnect()
                socket.close()
            self.__incomingConnections.clear()

    @pyqtSlot()
    def __newConnection(self):
        socket = self.__server.nextPendingConnection()
        print("NEW CONN", socket.peerAddress().toString(), socket.peerPort())
        socket.setSocketOption(QAbstractSocket.LowDelayOption, 1)
        socket.setSocketOption(QAbstractSocket.KeepAliveOption, 0)

        # socket.setProperty("port", socket.peerPort())
        # socket.setProperty("address", socket.peerAddress().toString())
        incomingConnection = _IncomingConnection()
        incomingConnection.socketDescriptor = socket.socketDescriptor()
        incomingConnection.socket = socket
        # incomingConnection.socket.setReadBufferSize(1024)
        incomingConnection.socket.readyRead.connect(self.__readData)
        incomingConnection.socket.disconnected.connect(self.__disconnected)
        incomingConnection.buffer = QByteArray()
        incomingConnection.address = socket.peerAddress().toString()
        incomingConnection.port = socket.peerPort()
        self.__incomingConnections[socket] = incomingConnection

    @pyqtSlot()
    def __readData(self):
        socket = self.sender()
        # print("READ", socket.peerAddress().toString(), socket.peerPort())
        # print("read data from", socket.objectName())
        incomingConnection = self.__incomingConnections.get(socket, None)
        if incomingConnection:
            bytesAvailable = socket.bytesAvailable()
            # if self.__serverPort != NetSettings.nodeCommandPort:
            #     print(bytesAvailable, "READING FROM SOCKET", socket.peerPort())
            if bytesAvailable:
                incomingConnection.buffer.append(socket.read(bytesAvailable))
                while incomingConnection.receivingPacketSize == 0 and incomingConnection.buffer.size() >= 4 \
                        or incomingConnection.receivingPacketSize > 0 and incomingConnection.buffer.size() >= incomingConnection.receivingPacketSize:
                    if incomingConnection.receivingPacketSize == 0 and incomingConnection.buffer.size() >= 4:
                        incomingConnection.receivingPacketSize = self.__bytesToInt(incomingConnection.buffer.left(4))
                        incomingConnection.buffer.remove(0, 4)
                    if incomingConnection.receivingPacketSize > 0 and incomingConnection.buffer.size() >= incomingConnection.receivingPacketSize:
                        packet = bytes(incomingConnection.buffer.left(incomingConnection.receivingPacketSize)).decode()
                        # if self.__signChecker.checkTran(packet):
                        self.newDataPacket.emit(incomingConnection.address, packet)
                        incomingConnection.buffer.remove(0, incomingConnection.receivingPacketSize)
                        incomingConnection.receivingPacketSize = 0
        else:
            print("Address disconnected already ")
            # raise Exception("ERROR WITH ADDRESS")

    @pyqtSlot()
    def __disconnected(self):
        socket = self.sender()
        print("disconnected from ", socket.objectName())
        self.__incomingConnections.pop(socket, None)

    @pyqtSlot()
    def __error(self):
        server = self.sender()
        print("ERROR", server.errorString())

    def __bytesToInt(self, data: QByteArray):
        temp = int().from_bytes(data, byteorder="little")
        return temp

