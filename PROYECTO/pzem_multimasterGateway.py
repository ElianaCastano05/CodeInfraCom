import minimalmodbus
import serial
import time
import requests

PORT = 'COM9'
BAUDRATE = 9600

ADDRESSES = [21, 22, 23]

URL = 'http://10.245.95.60:1880/tableroIngeniero'
INTERVALO = 2


def make_instrument(addr):
    ins = minimalmodbus.Instrument(
        PORT,
        addr,
        mode=minimalmodbus.MODE_RTU
    )

    ins.serial.baudrate = BAUDRATE
    ins.serial.bytesize = 8
    ins.serial.parity = serial.PARITY_NONE
    ins.serial.stopbits = 1
    ins.serial.timeout = 1.0

    ins.clear_buffers_before_each_transaction = True

    return ins


def read_pzem(ins):

    regs = ins.read_registers(0x0000, 9, functioncode=4)
    voltage = round(regs[0] * 0.1, 1)
    current = round((regs[2] << 16) | regs[1]) * 0.001
    power = round((regs[4] << 16) | regs[3]) * 0.1
    energy = round((regs[6] << 16) | regs[5])
    frequency = round(regs[7] * 0.1, 1)
    power_factor = round(regs[8] * 0.01,2)

    return {
        "voltage": f"{voltage:.2f}",
        "current": f"{current:.3f}",
        "energy_kWh": f"{energy:.2f}"
        
    }


instruments = [make_instrument(a) for a in ADDRESSES]

print(f"Enviando datos a {URL}")

while True:

    for idx, ins in enumerate(instruments):

        try:

            data = read_pzem(ins)

            payload = {
                "meter_id": ADDRESSES[idx], **data}

            r = requests.post(
                URL,
                json=payload,
                timeout=5
            )

            print(
                f"PZEM-{ADDRESSES[idx]} -> "
                f"{r.status_code} -> "
                f"{payload}")

        except Exception as ex:

            print(f"PZEM-{ADDRESSES[idx]} ERROR: {ex}")

        time.sleep(0.1)

    print('---')
    time.sleep(INTERVALO)