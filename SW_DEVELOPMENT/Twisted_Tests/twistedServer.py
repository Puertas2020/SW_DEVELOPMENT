#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import struct

### Protocol Implementation

# This is just about the simplest possible protocol


class Echo(Protocol):
    def dataReceived(self, data):
        """
        As soon as any data is received, write it back.
        """
        # tempData = struct.unpack("<HH",data)
        # print(tempData)

        if data[1] == 1:
            # print("tadaa")
            self.transport.write(b"It was a one")
            self.transport.write(b"1")
        elif data == "2":
            self.transport.write(b"It was a two")
            self.transport.write(b"2")
        else:
            self.transport.write(data)




def main():
    f = Factory()
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()


if __name__ == "__main__":
    main()