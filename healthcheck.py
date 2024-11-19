from config import CENTRAL_IP, REPLICA_IP, HEALTH_CHECK_PORT, REPLICA_HEALTH_PORT, ACTIVATION_PORT
import zmq
import time
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
registro_salud = logging.getLogger('MonitorSalud')

def verificar_servidor(contexto, direccion_ip, puerto, tiempo_espera):
    socket = contexto.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect(f"tcp://{direccion_ip}:{puerto}")
    socket.setsockopt(zmq.RCVTIMEO, tiempo_espera)
    try:
        registro_salud.debug(f"Enviando ping a {direccion_ip}:{puerto}")
        socket.send_string("ping")
        respuesta = socket.recv_string()
        socket.close()
        return respuesta == "pong"
    except zmq.error.Again:
        registro_salud.debug(f"Timeout esperando respuesta de {direccion_ip}:{puerto}")
        socket.close()
        return False
    except Exception as error:
        registro_salud.error(f"Error verificando servidor: {error}")
        socket.close()
        return False

def monitorizar_salud():
    contexto = zmq.Context()
    MAX_INTENTOS = 3
    TIEMPO_ESPERA = 5000  # 5 segundos
    supervisando_primario = True
    
    while supervisando_primario:
        ip_actual = CENTRAL_IP
        puerto_actual = HEALTH_CHECK_PORT
        fallos = 0
        
        for intento in range(MAX_INTENTOS):
            registro_salud.info(f"Verificando servidor principal (intento {intento + 1}/{MAX_INTENTOS})")
            
            if verificar_servidor(contexto, ip_actual, puerto_actual, TIEMPO_ESPERA):
                registro_salud.info("El servidor principal respondió correctamente.")
                break
            else:
                fallos += 1
                registro_salud.warning(f"El servidor principal no responde. Fallo {fallos}/{MAX_INTENTOS}")
                
                if fallos == MAX_INTENTOS:
                    registro_salud.error("El servidor principal no responde, activando la réplica...")
                    if activar_respaldo():
                        registro_salud.info("La réplica ha sido activada exitosamente.")
                        registro_salud.info("Finalizando monitorización de salud, ya que la réplica está activa.")
                        return
                    else:
                        registro_salud.error("No se pudo activar la réplica.")
                
                time.sleep(1)
        
        time.sleep(2)

    contexto.term()

def activar_respaldo():
    contexto = zmq.Context()
    socket_activacion = contexto.socket(zmq.REQ)
    socket_activacion.connect(f"tcp://{REPLICA_IP}:{ACTIVATION_PORT}")
    socket_activacion.setsockopt(zmq.RCVTIMEO, 5000)

    try:
        registro_salud.info("Enviando señal de activación a la réplica...")
        socket_activacion.send_string("ping")
        respuesta = socket_activacion.recv_string()
        return respuesta == "OK_ACTIVATED"
    except zmq.error.Again:
        registro_salud.error("La réplica no respondió a la activación.")
        return False
    except zmq.error.ZMQError as error:
        registro_salud.error(f"Error al activar la réplica: {error}")
        return False
    finally:
        socket_activacion.close()

if __name__ == "__main__":
    monitorizar_salud()
