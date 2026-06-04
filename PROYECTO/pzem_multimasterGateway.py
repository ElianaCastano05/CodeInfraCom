import time
import requests

from pzem_multimaster import (
    read_pzem,
    instruments
)

SLAVES = [21, 22, 23]

URL_DASHBOARD = "http://127.0.0.1:1880/meter"

CICLO = 2.0

print("Gateway iniciando")


while True:
    for idx, slave in enumerate(SLAVES):

        try:
            medidas = read_pzem(
            instruments[idx]
            )
            datos = {
                "meter_id": slave,
                "voltage": medidas["V"],
                "Corriente": medidas["I"],
                "Energia": medidas["E"],
            }

            print("Enviado:",datos) 

            r = requests.post(URL_DASHBOARD, json=datos, timeout=3)

            #print("Respuesta:", r.status_code)

        except Exception as exception:
            print(
                f"[{slave}] ERROR:",exception)
        time.sleep(0.1)
    print("--- ciclo completado ---")

    time.sleep(CICLO)