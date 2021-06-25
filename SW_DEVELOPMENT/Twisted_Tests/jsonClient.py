from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.internet.protocol import ReconnectingClientFactory


import json


class JsonClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        id = response.peer
        self.factory.resetDelay()
        JsonClientProtocol.connectionMadeCallback(self.sendJson, self, id)

    def onConnecting(self, transport_details):
        return None  # ask for defaults

    def sendJson(self, value):
        try:
            jsonResult = json.dumps(value)
        except ValueError:
            print("Message not serializable")
        else:
            self.sendMessage(jsonResult)

    def onOpen(self):
        pass

    def onMessage(self, payload, isBinary):
        try:
            jsonResult = json.loads(payload)
        except ValueError:
            print("Message not deserializable")
        else:
            JsonClientProtocol.setDataCallback(jsonResult)

    def connectionLost(self, reason):
        JsonClientProtocol.connectionLostCallback(reason)

    def onClose(self, wasClean, code, reason):
        JsonClientProtocol.connectionLostCallback(reason)


class WebSocketReconnectingClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = None

    def clientConnectionFailed(self, connector, reason):
        self.connectedToCentralSystem = False
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        self.connectedToCentralSystem = False
        self.retry(connector)


class JsonClient(object):
    SEND_FREQ = 0.1
    MAX_DELAY = 1

    def __init__(self, server, port, loopingCall, items):

        url = "ws://{}:{}".format(server, port)
        factory = WebSocketReconnectingClientFactory(url)
        factory.maxDelay = 5
        factory.protocol = JsonClientProtocol
        factory.protocol.connectionMadeCallback = self._connectionMade
        factory.protocol.connectionLostCallback = self._connectionLost
        factory.protocol.setDataCallback = self._dataReceived

        self.loopingCall = loopingCall
        self.items = items
        self.sendCallback = {}

        self.clientTask = self.loopingCall(self._update)
        self.clientTask.start(self.SEND_FREQ)

        connectWS(factory)

    def _connectionMade(self, sendCallback, protocol, id):
        self.sendCallback = sendCallback
        print("Websocket connection made - protocol: {}, id: {}".format(protocol, id))
        if self.connectionMadeCallback:
            self.connectionMadeCallback()

    def _dataReceived(self, resultDict):
        print(resultDict)

    def addTxMethod(self, methodPath, value):
        self._txMethods[methodPath] = value

    def _update(self):
        txItems = self.items
        # print(txItems)
        # self.sendCallback(txItems)

    def _connectionLost(self, reason):
        self.sendCallback = None


if __name__ == '__main__':
    from twisted.internet.task import LoopingCall
    from twisted.internet import reactor
    import json

    server = "127.0.0.1"
    port = 9000

    x = {
        "name": "John",
        "age": 30,
        "city": "New York"
    }

    y = json.dumps(x)



    loopingCall = LoopingCall

    jsonClient = JsonClient(server,port, loopingCall,y)
    reactor.run()
