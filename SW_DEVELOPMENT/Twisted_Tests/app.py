from twisted.internet import reactor
import twistedCliect2
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol


if __name__ == "__main__":
    app = twistedCliect2()
    point = TCP4ClientEndpoint(reactor, "localhost", 1234)
    d = connectProtocol(point, app.Greeter())
    d.addCallback(app.gotProtocol)
    reactor.run()