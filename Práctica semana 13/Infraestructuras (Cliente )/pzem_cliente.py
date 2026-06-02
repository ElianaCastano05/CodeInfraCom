# pzem_cliente.py
# Recibe ADU Modbus crudo por UDP y aplica las escalas del PZEM-014

import socket
import struct

UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))

print(f"Escuchando en UDP:{UDP_PORT}...\n")

def decode_pzem(adu: bytes) -> dict:
    if len(adu) < 23:
        return {'error': f'trama corta: {len(adu)} bytes'}

    addr    = adu[0]
    fc      = adu[1]
    n_bytes = adu[2]   # debe ser 18 (9 registros × 2 bytes)

    # 9 registros big-endian de 16 bits cada uno
    regs = struct.unpack('>9H', adu[3:21])

    # Escalas según datasheet PZEM-014
    voltaje    =  regs[0] * 0.1
    corriente  = ((regs[2] << 16) | regs[1]) * 0.001
    potencia   = ((regs[4] << 16) | regs[3]) * 0.1
    energia    =  (regs[6] << 16) | regs[5]
    frecuencia =  regs[7] * 0.1
    fp         =  regs[8] * 0.01

    return {
        'esclavo'  : f"{addr}",
        'V'        : round(voltaje,    1),
        'I'        : round(corriente,  3),
        'P'        : round(potencia,   1),
        'E'        : energia,
        'f'        : round(frecuencia, 1),
        'PF'       : round(fp,         2),
        'raw'      : adu.hex(' ')   # para comparar con Wireshark / LA1010
    }

while True:
    data, (ip_origen, _) = sock.recvfrom(256)
    r = decode_pzem(data)

    if 'error' in r:
        print(f"Error desde {ip_origen}: {r['error']}")
        continue

    print(f"Esclavo {r['esclavo']}  |  "
          f"{r['V']:6.1f} V  "
          f"{r['I']:6.3f} A  "
          f"{r['P']:7.1f} W  "
          f"{r['f']:5.1f} Hz  "
          f"PF={r['PF']:.2f}")
    print(f"  RAW: {r['raw']}\n")
