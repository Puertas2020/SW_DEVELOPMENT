#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall
import struct
import json


class EchoClientString(Int32StringReceiver):

    def connectionMade(self):
        self.state = 0

        # LineReceiver.setRawMode(self)

        # self.sendString(struct.pack("<H",0))
        self.lc = LoopingCall(self.sendSomething)
        self.lc.start(0.3)

    def dataReceived(self, data):
        # server_msg_dict = json.loads(data)
        # print(struct.unpack("d",data))
        pass

    def stringReceived(self, msg):
        server_msg_dict = json.loads(msg)
        print(server_msg_dict)
        # job = server_msg_dict["job"]
        # index = server_msg_dict["index"]
        # filestring = server_msg_dict["file"]

        # result = {"a": 1, "b": 2, "c": 3}
        # result_msg = {"result": result}

        # result_str = json.dumps(result_msg)
        # self.transport.write(result_str)

    def sendSomething(self):
        result = 3
        index = 1
        result_msg = { "result" : result, "jidx" : index }
        result_str = json.dumps(result_msg)
        stringtest = "sdfsdf"
        # print(result_str)
        # self.transport.write(bytes(result_str))
        self.sendString(b"sda")
        # self.sendString(struct.pack("<H",0))


class EchoClient(LineReceiver):
    end = b"Bye-bye!"

    def connectionMade(self):
        self.state = 0

        LineReceiver.setRawMode(self)

        self.sendLine(b"Connection established")
        self.lc = LoopingCall(self.sendSomething)
        self.lc.start(0.3)

    def rawDataReceived(self, data):
        print(data)

    def lineReceived(self, line):
        print("receive:", line)
        if line == self.end:
            self.transport.loseConnection()
        elif line == b"1":
            self.sendLine(b"2")
        elif line == b"2":
            self.sendLine(self.end)
        else:
            pass

    def sendSomething(self):
        if self.state == 0:
            self.sendLine(b"0")
            self.state = 1
        elif self.state == 1:
            self.sendLine(b"1")
            self.state = 2
        elif self.state == 2:
            self.sendLine(b"2")
            self.state = 0
        else:
            pass


class EchoClientFactory(ClientFactory):
    # protocol = EchoClient
    protocol = EchoClientString

    def __init__(self):
        self.done = Deferred()
        self.protocol = EchoClientFactory.protocol

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason.getErrorMessage())
        self.done.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print("connection lost:", reason.getErrorMessage())
        self.done.callback(None)

    def doSomething(self):
        self.protocol.sendSomething(b"XXX")


def main(reactor):
    factory = EchoClientFactory()
    reactor.connectTCP("localhost", 7000, factory)
    return factory.done


if __name__ == "__main__":
    task.react(main)