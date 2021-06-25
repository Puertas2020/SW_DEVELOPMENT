from autobahn.twisted.websocket import WebSocketClientProtocol
import json
import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory
from twisted.internet.task import LoopingCall


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        MyClientProtocol.connectionMadeCallbacka(self.sendJson)      # Nummer 2: Die Method wird hier aufgerufen -> _callBack von unten und die interne Method sendJson wird ubergegeben
        self.sendMessage(u"Client initiated".encode('utf8'))

    def sendJson(self, value):
        try:
            jsonResult = json.dumps(value, ensure_ascii=False).encode('utf8')
        except ValueError:
            print("Message not serializable")
        else:
            self.sendMessage(jsonResult)

    # def onMessage(self, payload, isBinary):
        # pass
        # if isBinary:
        #     print("Binary message received: {0} bytes".format(len(payload)))
        # else:
        #     print("Text message received: {0}".format(payload.decode('utf8')))

    # @staticmethod
    def sendSomething(self):
        self.sendMessage(u"Test hier".encode('utf8'))


class etwas(object):
    def __init__(self):
        log.startLogging(sys.stdout)
        factory = WebSocketClientFactory()
        factory.protocol = MyClientProtocol
        factory.protocol.connectionMadeCallbacka = self._connectionMade  # Nummer 1: Gibt die Method mit

        self.sendCallback = None

        self.counter = 0

        reactor.connectTCP("127.0.0.1", 9000, factory)
        reactor.run()

    def _connectionMade(self, sendCallback):                             # Nummer 3: Die Methode sendJson wird hier ubernommen und in dieses Object geerbt
        self.sendCallback = sendCallback

        self.clientTask = LoopingCall(self.sendData)
        self.clientTask.start(0.3)

    def sendData(self):
        self.item = {"result": self.counter}
        self.sendCallback(self.item)                                        # Nummer 4: Nun kann die geerbte sendCallback (sendJson) vom Protokoll verwendet werden
        self.counter += 1

if __name__ == '__main__':
    test = etwas()


