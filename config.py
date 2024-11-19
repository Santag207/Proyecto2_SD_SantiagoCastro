from dotenv import load_dotenv
import os
load_dotenv()

# Configuración de IPs - localhost por defecto, cambiar para configuración distribuida
IP_BROKER = os.getenv('BROKER_IP', 'localhost')
IP_REPLICA = os.getenv('REPLICA_IP', 'localhost')  
IP_PRINCIPAL = os.getenv('CENTRAL_IP', 'localhost')

# Configuración de Puertos (Modificados)
PUERTO_BROKER_PUB = int(os.getenv('BROKER_PUB_PORT', 7005))
PUERTO_BROKER_SUB = int(os.getenv('BROKER_SUB_PORT', 7006))
PUERTO_SERVIDOR_PRINCIPAL = int(os.getenv('CENTRAL_PORT', 7001))
PUERTO_SERVIDOR_REPLICA = int(os.getenv('REPLICA_PORT', 7002))
PUERTO_MONITOREO_SALUD = int(os.getenv('HEALTH_CHECK_PORT', 7008))
PUERTO_SALUD_REPLICA = int(os.getenv('REPLICA_HEALTH_PORT', 7009))
PUERTO_ACTIVACION = int(os.getenv('ACTIVATION_PORT', 7011))
BASE_PUERTOS_TAXI = int(os.getenv('TAXI_PORT_BASE', 8000))
