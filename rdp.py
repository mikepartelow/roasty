import json
import socket
import struct
import time
import logging

# https://rainfroginc.com/documentation/rdp-roastmaster-datagram-protocol
# https://rainfroginc.com/wordpress/wp-content/uploads/2017/03/RDP-Datasheet.pdf

class RDP:
    MULTICAST_GROUP = '224.0.0.1'
    MULTICAST_PORT  = 5050

    EVENT_TYPE_TEMPERATURE  = 3
    EVENT_TYPE_CONTROL      = 4

    CHANNEL_BEAN_TEMP       = 1
    CHANNEL_ENV_TEMP        = 2
    CHANNEL_HEATER_CONTROL  = 3
    CHANNEL_FAN_CONTROL     = 4

    RP_META_BEAN_TEMP       = 3000
    RP_META_ENV_TEMP        = 3001
    RP_META_ELECTRIC_LEVEL  = 4001
    RP_META_FAN_SPEED       = 4003

    def __init__(self, logger=logging):
        self._epoch = 9.0
        self._peer = None
        self.logger = logger

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
        self.logger.info("sent to %s: %s", address[0], payload)

    def handshake(self):
        dg = self.datagram(payload=[dict(RPChannel=1, RPEventType=1),])
        self.sendudp(dg, address=self.MULTICAST_GROUP)

        while True:
            data, address = self.sock.recvfrom(1024)
            if address[0] != socket.gethostbyname(socket.gethostname()):
                self.logger.debug("ack from %s: %s", address, data)
                self._peer = address[0]
                self.logger.info("found Roastmaster at %s", self._peer)
                break

    def send_values(self, bean_temp, env_temp, heater, fan):
        dg = self.datagram(payload=[
                                    dict(RPChannel=self.CHANNEL_BEAN_TEMP,
                                         RPEventType=self.EVENT_TYPE_TEMPERATURE,
                                         RPMetaType=self.RP_META_BEAN_TEMP,
                                         RPValue=bean_temp),
                                    dict(RPChannel=self.CHANNEL_ENV_TEMP,
                                         RPEventType=self.EVENT_TYPE_TEMPERATURE,
                                         RPMetaType=self.RP_META_ENV_TEMP,
                                         RPValue=env_temp),])
                                    # dict(RPChannel=self.CHANNEL_HEATER_CONTROL,
                                    #      RPEventType=self.EVENT_TYPE_CONTROL,
                                    #      RPMetaType=self.RP_META_ELECTRIC_LEVEL,
                                    #      RPValue=heater),
                                    # dict(RPChannel=self.CHANNEL_FAN_CONTROL,
                                    #      RPEventType=self.EVENT_TYPE_CONTROL,
                                    #      RPMetaType=self.RP_META_FAN_SPEED,
                                    #      RPValue=fan),
                                    # ])

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
            RPEpoch=self.epoch(),
            RPPayload=payload,
        )

        return json.dumps(d)

logging.basicConfig(level=logging.INFO)
logging.info("hello")
rdp = RDP()
rdp.handshake()

time.sleep(1)

while True:
    rdp.send_values(bean_temp=123.0, env_temp=153.0, heater=90.0, fan=4.0)
    time.sleep(1)
    rdp.send_values(bean_temp=125.0, env_temp=153.0, heater=90.0, fan=0.0)
    time.sleep(1)
    rdp.send_values(bean_temp=127.0, env_temp=155.0, heater=80.0, fan=0.0)
    time.sleep(1)
    rdp.send_values(bean_temp=129.0, env_temp=157.0, heater=80.0, fan=0.0)
    time.sleep(1)
    rdp.send_values(bean_temp=131.0, env_temp=159.0, heater=80.0, fan=0.0)
    time.sleep(1)
    rdp.send_values(bean_temp=133.0, env_temp=161.0, heater=70.0, fan=0.0)
    time.sleep(1)
    rdp.send_values(bean_temp=138.0, env_temp=166.0, heater=70.0, fan=3.0)
    time.sleep(1)
    rdp.send_values(bean_temp=141.0, env_temp=171.0, heater=70.0, fan=3.0)
    time.sleep(1)
    rdp.send_values(bean_temp=150.0, env_temp=174.0, heater=60.0, fan=3.0)
    time.sleep(1)
    rdp.send_values(bean_temp=151.0, env_temp=177.0, heater=60.0, fan=4.0)
    time.sleep(1)

# TODO:
#  - better epochs
#  - error recovery (keep on sending no matter what) (maybe do this in combined hottop/roastmaster code)
#  - figure out minimum send frequency, don't drop below or RoastMaster barfs