import minimalmodbus
import time
import serial
from serial.tools import list_ports

# 1) Mostrar puertos para confirmar
print("Puertos serie disponibles:")
for p in list_ports.comports():
    print(f" - {p.device}: {p.description}")

PORT = "COM9"   # <-- AJUSTE al COM detectado
ADDR = 22      # Dirección Modbus del PZEM-016
NEW_ADDR=22

ins = minimalmodbus.Instrument(PORT, ADDR, mode=minimalmodbus.MODE_RTU)
ins.serial.baudrate = 9600
ins.serial.bytesize = 8
ins.serial.parity   = serial.PARITY_NONE  # pruebe PARITY_EVEN si no responde
ins.serial.stopbits = 1
ins.serial.timeout  = 1.0
ins.clear_buffers_before_each_transaction = True

# 1) Escribir nueva dirección en Holding Register 0x0002 con función 0x06
ins.write_register(0x0002, NEW_ADDR, number_of_decimals=0, functioncode=6, signed=False)
time.sleep(0.2)
print(f"Dirección cambiada: {ADDR} → {NEW_ADDR}")
