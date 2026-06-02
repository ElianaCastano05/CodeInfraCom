# meter_sim.py — Simulador de medidor PZEM-014
# Fase 1: valores aleatorios. Fase 2: reemplazar con datos reales del PZEM.

import time, random, requests

URL       = 'http://127.0.0.1:1880/meter'
METER_ID  = 1
INTERVALO = 15   # segundos entre envíos

def generar_muestra():
    return {
        "meter_id"   : METER_ID,
        "voltage"    : round(random.uniform(110.0, 123.0), 1),  # V AC típico
        "current"    : round(random.uniform(0.5,   5.0),   2),  # A
        "energy_kWh" : round(random.uniform(0.0,   100.0), 3),  # kWh acumulado
    }

if __name__ == "__main__":
    print(f'Simulador iniciado → {URL}')
    print(f'Enviando cada {INTERVALO} segundos. Ctrl+C para detener.\n')
    while True:
        datos = generar_muestra()
        try:
            r = requests.post(URL, json=datos, timeout=5)
            print(f'POST /meter → {r.status_code}  {datos}')
        except Exception as e:
            print(f'Error de conexión: {e}')
        time.sleep(INTERVALO)
