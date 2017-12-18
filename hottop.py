import serial
import binascii
import time
import datetime
import logging

def murican(x):
    return 9.0/5.0 * x + 32

def hex2int(h1, h2=""):
    return int(binascii.hexlify(h1+h2), 16)

class Hottop:
    def __init__(self, logger=logging, device='/dev/cu.usbserial-DA01P4X7'):
        self.logger = logger
        self._port = serial.Serial(device, 115200, timeout=1)

    def openport(self):
        # try:
            if not self._port.isOpen():
                self._port.open()
        # except Exception:
            # pass

    def closeport(p):
        # try:
            if self._port is not None and self._port.isOpen():
                self._port.close()
        # except Exception:
            # pass

    def monitor(self, reporter, interval_seconds=1, loop_while=True):
        self.logger.info("monitoring Hottop")

        while loop_while:
            self.openport()
            if self._port.isOpen():
                self._port.flushInput()
                self._port.flushOutput()
                data = self._port.read(36)

                reporter.report_data(data)

                if len(data) != 36:
                    self.closeport()
                else:
                    P0, P1, P35 = hex2int(data[0]), hex2int(data[1]), hex2int(data[35])
                    chksum = sum([hex2int(c) for c in data[:35]]) & 0xFF

                    if P0 != 165 or P1 != 150 or P35 != chksum:
                        self.closeport()
                    else:
                        heater = hex2int(data[10]) # 0-100
                        fan = hex2int(data[11])
                        main_fan = hex2int(data[12]) # 0-10
                        env_temp = hex2int(data[23],data[24]) # in C
                        bean_temp = hex2int(data[25],data[26]) # in C

                        self.logger.info("BT: %sC/%sF ET: %sC/%sF Heat: %s Fan: %s",
                                            bean_temp, int(murican(bean_temp)),
                                            env_temp, int(murican(env_temp)),
                                            heater, fan)

                        reporter.report_values(bean_temp_in_c=bean_temp, env_temp_in_c=env_temp, heater=heater, fan=fan)

            time.sleep(interval_seconds)