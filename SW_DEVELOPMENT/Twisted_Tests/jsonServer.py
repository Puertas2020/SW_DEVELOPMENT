import json
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS


class JsonServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        JsonServerProtocol.connectionMadeCallback(request.peer)

    def onOpen(self):
        pass

    def onMessage(self, payload, isBinary):
        try:
            jsonResult = json.loads(payload)
        except ValueError:
            print("Message not deserializable")
        else:
            if isinstance(jsonResult, dict):
                JsonServerProtocol.setDataCallback(jsonResult, raw=payload)
            else:
                print("Message does not contain dict")

        items = JsonServerProtocol.getDataCallback()
        sendMsg = json.dumps(items, skipkeys=True, default=JsonServerProtocol.defaultObjEncoder)
        self.sendMessage(sendMsg)
        self.sentDataCallback(sendMsg)

    def connectionLost(self, reason):
        JsonServerProtocol.connectionLostCallback(reason)
        self._connectionLost(reason)

    def onClose(self, wasClean, code, reason):
        JsonServerProtocol.connectionLostCallback(reason)


class JsonServer(object):
    MAIN_FREQ = 0.2
    MAX_DELAY = 1

    def __init__(self, environment, port, items=None, encode_types=None, logger=None):
        self.encodeObjects = encode_types or []
        self.port = port
        self.items = items if items is not None else {"Empty": "None"}





        self.serverTask = self.task.LoopingCall(self._update)
        self.serverTask.start(self.MAIN_FREQ)

        url = "ws://127.0.0.1:{}".format(self.port)
        factory = WebSocketServerFactory(url, reactor=environment.reactor)
        factory.protocol = JsonServerProtocol
        factory.protocol.getDataCallback = self._getData
        factory.protocol.setDataCallback = self._dataReceived
        factory.protocol.sentDataCallback = self._dataSent
        factory.protocol.defaultObjEncoder = self._objEncoder
        factory.protocol.connectionMadeCallback = self._connectionMade
        factory.protocol.connectionLostCallback = self._connectionLost
        factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=2, maxConnections=1)
        listenWS(factory)


    def _dataReceived(self, resultDict, raw=None):
        rxCount = storeData(resultDict, target=self.items)
        methods = resultDict.get(TAG_METHODS, {})
        for key, value in methods.items():
            path = key.split(".")
            if len(path) > 1:
                obj = self.items.get(path[0])
                method = getattr(obj, path[1], None)
                if callable(method):
                    try:
                        method(value)
                    except Exception as e:
                        self.logger.log("Exception while call {} in object {} - {}".format(path[1], path[0], e))
                elif method:
                    self.logger.log("Attribute {} in object {} not callable".format(path[1], path[0]))
                else:
                    self.logger.log("Attribute {} in object {} not found".format(path[1], path[0]))

        if self.logger.debug and raw:
            self.logger.log("Rx: " + raw)

        if rxCount > 0:
            self._stopwatch.start()
            return True
        else:
            self.logger.log("Received message did not contain matching data")
            return False

    def _connectionMade(self, peer):
        self.logger.log("WebSocket connection made: {}".format(peer))

    def _connectionLost(self, reason):
        self.logger.log("WebSocket connection closed: {}".format(reason))

    def _update(self):
        timeout = not self._stopwatch.running() or self._stopwatch.elapsed() > self.MAX_DELAY
        if timeout and not self.timeout:
            self.logger.log("Message Timeout (>{}s)".format(self.MAX_DELAY))
        self.timeout = timeout


if __name__ == '__main__':
    import sys

    from twisted.python import log
    from twisted.internet import reactor, task
    from Environment import Environment
    from powerunit.PowerUnitN import PowerUnitInterface

    from utils.TaskManager import TaskManager
    import Time
    import utils.Subprocess
    import utils.Platform

    from unittests.ECPTestHelpers import MockerLogger

    loggers = MockerLogger()

    chnAuxiliaryProcessRx = utils.Subprocess.Channel()
    chnAuxiliaryProcessTx = utils.Subprocess.Channel()
    router = utils.Subprocess.Router(reactor, chnAuxiliaryProcessTx, chnAuxiliaryProcessRx)
    timemaster = Time.TYPE_MASTER_PROCESS
    task2 = TaskManager(reactor, "TaskManagerMain", 0.05)
    platform = utils.Platform.getPlatform()

    environment = Environment(macAddress="", platform=platform, reactor=reactor,
                              task2=task2, router=router, warningLoggerActive=False, loggers=loggers)


    def myprint(x):
        print(x)


    stPU0 = PowerUnitInterface()
    stPU0._test = "dd"
    stPU0.setMaxACPower = myprint

    stPU1 = PowerUnitInterface()

    log.startLogging(sys.stdout)
    logger = loggers.getLogger("PowerSourceServer")
    JsonServer(environment, port=9200, items={"PowerUnit0": stPU0, "PowerUnit1": stPU1},
               encode_types=["PowerUnitInterface"], logger=logger)

    # note to self: if using putChild, the child must be bytes...

    reactor.run()
