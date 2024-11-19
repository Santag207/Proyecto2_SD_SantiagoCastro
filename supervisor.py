import subprocess
import time
import os
import signal

# Función para verificar si el proceso del Broker está en ejecución
def verificar_proceso_broker():
    try:
        resultado = subprocess.run(['pgrep', '-f', 'broker.py'], stdout=subprocess.PIPE)
        if resultado.stdout:  # Si hay salida, significa que el Broker está activo
            identificador = int(resultado.stdout.decode().strip())
            print(f"Broker detectado en ejecución con PID: {identificador}")
            return identificador
        else:
            return None
    except Exception as error:
        print(f"Error al intentar verificar el estado del Broker: {error}")
        return None

# Función para iniciar el proceso del Broker
def iniciar_proceso_broker():
    print("Iniciando el proceso del Broker...")
    proceso = subprocess.Popen(['python', 'broker.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proceso

# Verificar si un proceso con un PID específico está funcionando
def validar_proceso_pid(pid):
    try:
        os.kill(pid, 0)  # Señal 0 solo valida si el proceso existe
        return True
    except OSError:
        return False

# Función principal para supervisar el Broker
def gestor_broker():
    pid_actual = verificar_proceso_broker()  # Comprobar si el Broker ya está corriendo
    proceso_broker = None

    if pid_actual:
        print(f"Supervisando el proceso del Broker existente con PID {pid_actual}")
    else:
        # Si el Broker no está activo, lo iniciamos
        proceso_broker = iniciar_proceso_broker()

    while True:
        if proceso_broker:
            # Si el supervisor inició el Broker, verificar su estado usando poll
            if proceso_broker.poll() is not None:  # Si poll() retorna algo, el proceso terminó
                print("El proceso del Broker se ha detenido. Reiniciando...")
                proceso_broker = iniciar_proceso_broker()
            else:
                print("El proceso del Broker está funcionando correctamente.")
        else:
            # Si supervisamos un Broker existente, validar su PID
            if not validar_proceso_pid(pid_actual):
                print("El proceso supervisado del Broker ha fallado. Reiniciando...")
                proceso_broker = iniciar_proceso_broker()

        time.sleep(3)  # Intervalo para verificar el estado

if __name__ == "__main__":
    gestor_broker()
