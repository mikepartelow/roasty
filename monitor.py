import serial
import binascii
import time
import datetime

def murican(x):
    return 9.0/5.0 * x + 32

def hex2int(h1,h2=""):
    return int(binascii.hexlify(h1+h2),16)

def openport(p):
    # try:
        if not p.isOpen():
            p.open()
    # except Exception:
        # pass

def closeport(p):
    try:
        if p is not None and p.isOpen():
            p.close()
    except Exception:
        pass


def configure_serial():
    return serial.Serial('/dev/cu.usbserial-DA01P4X7', 115200, timeout=1)

def monitor(sp, interval_seconds=1, binlog_prefix='binlog', humanlog_prefix='humanlog'):
    binlog_path = binlog_prefix + '.' + datetime.datetime.today().isoformat()
    humanlog_path = humanlog_prefix + '.' + datetime.datetime.today().isoformat()

    with open(binlog_path, 'wb') as binlog, open(humanlog_path, 'w') as humanlog:
        while True:
            openport(sp)
            if sp.isOpen():
                sp.flushInput()
                sp.flushOutput()
                r = sp.read(36)

                if len(r) != 36:
                    closeport(sp)
                else:
                    binlog.write(r)
                    humanlog.write(datetime.datetime.today().isoformat())

                    P0 = hex2int(r[0])
                    P1 = hex2int(r[1])
                    chksum = sum([hex2int(c) for c in r[:35]]) & 0xFF
                    P35 = hex2int(r[35])

                    if P0 != 165 or P1 != 150 or P35 != chksum:
                        closeport(sp)
                    else:
                        heater = hex2int(r[10]) # 0-100
                        fan = hex2int(r[11])
                        main_fan = hex2int(r[12]) # 0-10
                        env_temp = hex2int(r[23],r[24]) # in C
                        bean_temp = hex2int(r[25],r[26]) # in C

                        humanlog.write(",{}F,{}F,{},{}%".format(bean_temp, env_temp, main_fan, heater))

                        print("Bean Temp   : {}F".format(int(murican(bean_temp))))
                        print("Env Temp    : {}F".format(int(murican(env_temp))))
                        print("Fan:        : {}".format(main_fan))
                        print("Heater:     : {}%".format(heater))
                        print("\n")

                    humanlog.write("\n")

            time.sleep(interval_seconds)

sp = configure_serial()
try:
    monitor(sp, interval_seconds=5, binlog_prefix='./logs/binlog', humanlog_prefix='./logs/humanlog')
except KeyboardInterrupt:
    pass
