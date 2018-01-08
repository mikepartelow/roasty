import hottop
import rdp
import logging
import json

class Reporter:
    def __init__(self, rdp, logger=logging):
        self._rdp = rdp
        self.logger = logger

    def report_data(self, data):
        pass

    def report_values(self, bean_temp_in_c, env_temp_in_c, heater, fan):
        self._rdp.send_values(bean_temp_in_c, env_temp_in_c, heater, fan)

if __name__ == "__main__":
    try:
        with open('./roasty.json', 'r') as f:
            config = json.loads(f.read())
    except:
        config = {}

    logfilename = config.get('logfilename')
    device      = config.get('hottop device')

    logging.basicConfig(level=logging.DEBUG, filename=logfilename)

    rdp = rdp.RDP()
    
    rdp.handshake(addresses=["192.168.2.178","192.168.2.179",])
    
    rdp.handshake()

    reporter = Reporter(rdp)
    hottop   = hottop.Hottop(device=device)

    hottop.monitor(reporter)
