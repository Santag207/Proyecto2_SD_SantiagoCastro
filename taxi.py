from config import BROKER_IP, BROKER_PUB_PORT, TAXI_PORT_BASE
import zmq
import time
import random
import json
import sys
import logging
import socket

# Configuración del registro
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
registro_log = logging.getLogger("TaxiLog")

ARCHIVO_JSON = 'informacion_t.json'

# Funciones para manejo de datos en archivo
def leer_datos_archivo(archivo):
    try:
        with open(archivo, 'r') as f:
            contenido = json.load(f)
    except FileNotFoundError:
        contenido = {"taxis_registrados": []}
    return contenido

def escribir_datos_archivo(archivo, contenido):
    try:
        with open(archivo, 'w') as f:
            json.dump(contenido, f, indent=4)
    except Exception as err:
        registro_log.error(f"No se pudieron guardar los datos en {archivo}: {err}")

# Clase que representa un Taxi
class Vehiculo:
    def __init__(self, identificador, tamano_ciudad, posicion_x, posicion_y, velocidad, max_servicios):
        self.identificador = identificador
        self.tamano_ciudad = tamano_ciudad
        self.posicion_inicial = (posicion_x, posicion_y)
        self.x_actual = posicion_x
        self.y_actual = posicion_y
        self.velocidad_movimiento = velocidad
        self.servicios_maximos = max_servicios
        self.servicios_realizados = 0

    def actualizar_posicion(self):
        intervalo_movimiento = 30  
        distancia = (self.velocidad_movimiento * intervalo_movimiento) / 60  
        direccion = random.choice(["vertical", "horizontal"])

        if direccion == "vertical":
            nueva_x = max(0, min(self.x_actual + distancia, self.tamano_ciudad[0] - 1))
            if nueva_x != self.x_actual:
                self.x_actual = nueva_x
                registro_log.debug(f"Taxi {self.identificador} movido a posición ({self.x_actual:.1f}, {self.y_actual:.1f}).")
                return True
        else:
            nueva_y = max(0, min(self.y_actual + distancia, self.tamano_ciudad[1] - 1))
            if nueva_y != self.y_actual:
                self.y_actual = nueva_y
                registro_log.debug(f"Taxi {self.identificador} movido a posición ({self.x_actual:.1f}, {self.y_actual:.1f}).")
                return True
        return False

    def regresar_inicio(self):
        self.x_actual, self.y_actual = self.posicion_inicial
        registro_log.info(f"Taxi {self.identificador} regresó a su posición inicial {self.posicion_inicial}.")

# Función principal para manejar taxis
def gestionar_vehiculo(id_vehiculo, tamano_matriz, velocidad, max_servicios):
    contexto = zmq.Context()

    # Configuración de sockets
    socket_publicador = contexto.socket(zmq.PUB)
    socket_publicador.connect(f"tcp://{BROKER_IP}:{BROKER_PUB_PORT}")

    socket_receptor = contexto.socket(zmq.REP)
    socket_receptor.bind(f"tcp://*:{TAXI_PORT_BASE + id_vehiculo}")

    registro_log.info(f"Vehículo {id_vehiculo} escuchando en puerto {TAXI_PORT_BASE + id_vehiculo}")

    try:
        datos_vehiculo = leer_datos_archivo(ARCHIVO_JSON)

        vehiculo = Vehiculo(
            id_vehiculo,
            tamano_matriz,
            random.randint(0, tamano_matriz[0] - 1),
            random.randint(0, tamano_matriz[1] - 1),
            velocidad,
            max_servicios
        )

        while vehiculo.servicios_realizados < vehiculo.servicios_maximos:
            tiempo_inicio = time.time()

            # Mover el taxi
            if vehiculo.actualizar_posicion():
                registro_log.debug(f"Vehículo {vehiculo.identificador} cambió su ubicación.")
            
            # Publicar la posición
            info_publicada = {
                "identificador": vehiculo.identificador,
                "x_actual": round(vehiculo.x_actual, 1),
                "y_actual": round(vehiculo.y_actual, 1),
                "estado": "disponible",
                "servicios_completados": vehiculo.servicios_realizados
            }
            socket_publicador.send_string(f"ubicacion_vehiculo {vehiculo.identificador} {json.dumps(info_publicada)}")
            registro_log.info(f"Vehículo {vehiculo.identificador} publicó nueva posición: {info_publicada}")

            # Simular recepción de servicios
            poller = zmq.Poller()
            poller.register(socket_receptor, zmq.POLLIN)
            eventos = dict(poller.poll(1000))

            if eventos.get(socket_receptor) == zmq.POLLIN:
                servicio_recibido = socket_receptor.recv_string()
                registro_log.info(f"Vehículo {vehiculo.identificador} recibió servicio: {servicio_recibido}")
                socket_receptor.send_string(f"Vehículo {vehiculo.identificador} acepta servicio")

                time.sleep(random.uniform(1, 3))
                vehiculo.regresar_inicio()
                vehiculo.servicios_realizados += 1

            time.sleep(1)

    finally:
        socket_publicador.close()
        socket_receptor.close()
        contexto.term()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python taxi.py <id_vehiculo>")
        sys.exit(1)

    id_vehiculo = int(sys.argv[1])
    tamano_matriz = (10, 10)
    velocidad = random.choice([1, 2, 4])
    max_servicios = 3

    registro_log.info(f"Iniciando Vehículo {id_vehiculo} con velocidad {velocidad}.")
    gestionar_vehiculo(id_vehiculo, tamano_matriz, velocidad, max_servicios)
