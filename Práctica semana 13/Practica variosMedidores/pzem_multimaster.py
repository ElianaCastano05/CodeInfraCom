import minimalmodbus, serial, time

PORT      = 'COM9'          # <-- ajuste al COM real
BAUDRATE  = 9600
ADDRESSES = [21, 22, 23]   # direcciones de los tres PZEM

def make_instrument(addr):
    ins = minimalmodbus.Instrument(PORT, addr, mode=minimalmodbus.MODE_RTU)
    ins.serial.baudrate = BAUDRATE
    ins.serial.bytesize = 8
    ins.serial.parity   = serial.PARITY_NONE
    ins.serial.stopbits = 1
    ins.serial.timeout  = 1.0
    ins.clear_buffers_before_each_transaction = True
    return ins

def read_pzem(ins):
    regs = ins.read_registers(0x0000, 9, functioncode=4)
    v  = regs[0] * 0.1
    i  = ((regs[1] << 16) | regs[2]) * 0.001
    p  = ((regs[3] << 16) | regs[4]) * 0.1
    e  =  (regs[5] << 16) | regs[6]
    f  = regs[7] * 0.1
    pf = regs[8] * 0.01
    return dict(V=v, I=i, P=p, E=e, f=f, PF=pf)

instruments = [make_instrument(a) for a in ADDRESSES]

while True:
    for idx, ins in enumerate(instruments):
        try:
            data = read_pzem(ins)
            print(f'PZEM-{idx+1}: {data}')
        except Exception as ex:
            print(f'PZEM-{idx+1} ERROR: {ex}')
        time.sleep(0.1)   # pausa inter-esclavo
    print('---')
    time.sleep(2)         # ciclo de lectura cada 2 s
