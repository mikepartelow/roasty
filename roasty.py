import hottop
import rdp
import logging

class Reporter:
    def __init__(self, rdp, logger=logging):
        self._rdp = rdp
        self.logger = logger

    def report_data(self, data):
        pass

    def report_values(self, bean_temp_in_c, env_temp_in_c, heater, fan):
        self._rdp.send_values(bean_temp_in_c, env_temp_in_c, heater, fan)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    rdp = rdp.RDP()
    reporter = Reporter(rdp)
    hottop = hottop.Hottop()

    rdp.handshake()
    hottop.monitor(reporter)