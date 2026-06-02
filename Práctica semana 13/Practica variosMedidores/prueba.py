# pzem_multimaster_gateway.py
# Gateway: lee 3 PZEM-014 por RS-485 y reenvía ADU crudo via UDP broadcast

import serial
import socket
import struct
import time

# ── Configuración ────────────────────────────────────────
PORT      = 'COM9'       # Ajuste al COM real (Linux: '/dev/ttyUSB0')
BAUDRATE  = 9600
TIMEOUT   = 1.0
SLAVES    = [21, 22, 23]   # Direcciones Modbus de los 3 PZEM-014

UDP_IP    = '192.168.1.255'       # Broadcast de la subred
UDP_PORT  = 5000
CICLO     = 2.0                   # Segundos entre ciclos de lectura completos

# ── CRC-16 Modbus ────────────────────────────────────────
def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return struct.pack('<H', crc)   # little-endian, 2 bytes

# ── Construye petición Modbus RTU ────────────────────────
def build_request(slave: int) -> bytes:
    # FC=0x04, Start=0x0000, Count=0x0009 (9 registros del PZEM-014)
    pdu = struct.pack('>BBHH', slave, 0x04, 0x0000, 0x0009)
    return pdu + crc16(pdu)

# ── Verifica CRC de la respuesta ─────────────────────────
def crc_ok(frame: bytes) -> bool:
    if len(frame) < 3:
        return False
    payload  = frame[:-2]
    received = frame[-2:]
    return crc16(payload) == received

# ── Setup ────────────────────────────────────────────────
ser = serial.Serial(
    port     = PORT,
    baudrate = BAUDRATE,
    bytesize = serial.EIGHTBITS,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    timeout  = TIMEOUT
)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print(f"Gateway iniciado — Puerto: {PORT}  UDP: {UDP_IP}:{UDP_PORT}")
print(f"Esclavos: {[hex(s) for s in SLAVES]}\n")

# ── Bucle principal ──────────────────────────────────────
while True:
    for slave in SLAVES:
        try:
            # 1. Envía petición al bus RS-485
            req = build_request(slave)
            ser.reset_input_buffer()
            ser.write(req)

            # 2. Espera respuesta: 1+1+1+18+2 = 23 bytes
            #    (addr + FC + bytecount + 9 regs×2 + CRC)
            adu = ser.read(23)

            if len(adu) < 23:
                print(f"  [{hex(slave)}] Timeout — solo {len(adu)} bytes recibidos")
                continue

            if not crc_ok(adu):
                print(f"  [{hex(slave)}] CRC inválido: {adu.hex(' ')}")
                continue

            # 3. Reenvía el ADU crudo por UDP — sin modificar ningún byte
            sock.sendto(adu, (UDP_IP, UDP_PORT))
            print(f"  [{hex(slave)}] TX: {adu.hex(' ')}")

        except serial.SerialException as e:
            print(f"  [{hex(slave)}] Error serial: {e}")

        time.sleep(0.1)   # Pausa entre esclavos (inter-frame RS-485)

    print(f"  --- ciclo completado ---")
    time.sleep(CICLO)
