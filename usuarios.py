from config import CENTRAL_IP, CENTRAL_PORT, REPLICA_PORT, REPLICA_IP
import zmq
import time
import threading
import random

# Diccionario para rastrear el estado de los usuarios (activos o inactivos)
estado_usuarios = {}

# Clase para manejar solicitudes de usuarios
class Cliente:
    def __init__(self, id_cliente, pos_x, pos_y, tiempo_delay):
        self.id_cliente = id_cliente
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.tiempo_delay = tiempo_delay

    def solicitar_taxi(self, direccion_servidor):
        contexto = zmq.Context()
        socket_peticion = contexto.socket(zmq.REQ)
        socket_peticion.connect(direccion_servidor)

        estado_usuarios[self.id_cliente] = True
        tiempo_inicio = time.time()

        try:
            # Enviar solicitud
            mensaje = f"Cliente {self.id_cliente} en posición ({self.pos_x}, {self.pos_y}) solicita un taxi"
            socket_peticion.send_string(mensaje)
            print(f"{mensaje} usando el socket {socket_peticion.getsockopt(zmq.LAST_ENDPOINT)}.")

            # Esperar respuesta con un tiempo límite
            socket_peticion.setsockopt(zmq.RCVTIMEO, 15000)  # 15 segundos de timeout
            respuesta = socket_peticion.recv_string()
            tiempo_total = time.time() - tiempo_inicio

            print(f"Cliente {self.id_cliente} recibió respuesta: {respuesta} en {tiempo_total:.2f} segundos.")
            estado_usuarios[self.id_cliente] = False
            return True

        except zmq.error.Again:
            print(f"Cliente {self.id_cliente} no obtuvo respuesta en el tiempo esperado. Cancelando solicitud.")
            estado_usuarios[self.id_cliente] = False
            return False

        finally:
            socket_peticion.close()

    def iniciar(self):
        time.sleep(self.tiempo_delay)
        print(f"Cliente {self.id_cliente} listo para solicitar un taxi después de {self.tiempo_delay} segundos.")
        servidores = [
            (f"tcp://{CENTRAL_IP}:{CENTRAL_PORT}", "Servidor Principal"),
            (f"tcp://{REPLICA_IP}:{REPLICA_PORT}", "Servidor Réplica"),
        ]

        for direccion, descripcion in servidores:
            if self.solicitar_taxi(direccion):
                return
        print(f"Cliente {self.id_cliente} no fue atendido en ninguno de los servidores.")

# Clase generadora de múltiples clientes
class GeneradorClientes:
    def __init__(self, archivo_coordenadas):
        self.archivo_coordenadas = archivo_coordenadas

    def crear_clientes(self):
        hilos = []
        try:
            with open(self.archivo_coordenadas, 'r') as archivo:
                coordenadas = archivo.readlines()

            for indice, linea in enumerate(coordenadas):
                try:
                    pos_x, pos_y = map(int, linea.strip().split(','))
                    tiempo_random = random.randint(1, 5)  # Delay aleatorio entre 1 y 5 segundos
                    cliente = Cliente(indice, pos_x, pos_y, tiempo_random)
                    hilo = threading.Thread(target=cliente.iniciar)
                    hilos.append(hilo)
                    hilo.start()
                except ValueError:
                    print(f"Coordenadas inválidas en la línea {indice + 1}: {linea.strip()}")

        except FileNotFoundError:
            print(f"No se encontró el archivo {self.archivo_coordenadas}.")

        for hilo in hilos:
            hilo.join()

if __name__ == "__main__":
    archivo = "coordenadas_usuarios.txt"
    generador = GeneradorClientes(archivo)
    generador.crear_clientes()
