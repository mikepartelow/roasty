import json
import socket
import struct
import time

# https://rainfroginc.com/documentation/rdp-roastmaster-datagram-protocol
# https://rainfroginc.com/wordpress/wp-content/uploads/2017/03/RDP-Datasheet.pdf

class RDP:
    MULTICAST_GROUP = '224.0.0.1'
    MULTICAST_PORT  = 5050

    EVENT_TYPE_TEMPERATURE = 3

    def __init__(self):
        self._epoch = 9.0
        self._peer = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # for sending
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)

        # for receiving
        self.sock.bind(('', self.MULTICAST_PORT))
        group = socket.inet_aton(self.MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def sendudp(self, payload, address=None):
        if not isinstance(payload, str):
            raise ArgumentError("payload should be a str")

        if address is None:
            address = self._peer

        self.sock.sendto(payload, (address, self.MULTICAST_PORT))
        print("sent to {}: {}\n".format(address, payload))

    def handshake(self):
        dg = self.datagram(payload=[dict(RPChannel=1, RPEventType=1),])
        self.sendudp(dg, address=self.MULTICAST_GROUP)

        while True:
            data, address = self.sock.recvfrom(1024)
            if address[0] != socket.gethostbyname(socket.gethostname()):
                print "received %s bytes from %s\n" % (len(data), address)
                print data
                print "\n"

                self._peer = address[0]
                print("set peer to {}\n".format(self._peer))
                break

    def send_value(self, value):
        dg = self.datagram(payload=[dict(RPChannel=1, RPEventType=self.EVENT_TYPE_TEMPERATURE, RPValue=value)])
        self.sendudp(dg)

    def epoch(self):
        self._epoch += 1
        return self._epoch

    def datagram(self, payload):
        if not isinstance(payload, list) or not isinstance(payload[0], dict):
            raise ArgumentError("payload should be a list of dicts")

        d = dict(
            RPVersion="RDP_1.0",
            RPSerial="RDP0",
            RPChannel=1,
            RPEpoch=self.epoch(),
            RPPayload=payload,
        )

        return json.dumps(d)

rdp = RDP()
rdp.handshake()

time.sleep(1)

value = 123.0
while True:
    value += 1.0
    rdp.send_value(value)
    time.sleep(1)


# dg = rdp.datagram([dict(RPEventType=1),])


# import socket
# import struct

# MCAST_GRP = '224.0.0.1'
# MCAST_PORT = 5050
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
# sock.sendto(dg, (MCAST_GRP, MCAST_PORT))

# import binascii

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# try:
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# except AttributeError:
#     pass
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

# sock.bind((MCAST_GRP, MCAST_PORT))
# host = socket.gethostbyname(socket.gethostname())
# sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
# sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
#                    socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))

# while 1:
#     print("loop")
#     try:
#       data, addr = sock.recvfrom(1024)
#     except socket.error, e:
#       print 'Expection'
#       hexdata = binascii.hexlify(data)
#       print 'Data = %s' % hexdata